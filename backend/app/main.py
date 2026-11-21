import os
from uuid import UUID

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from .agent_gateway.client import AgentServerClient
from .agent_gateway.models import CreateAgentRun
from .auth.service import AuthError, AuthService
from .observability.benchmark import BenchmarkStore, RetrievalCase, retrieval_scores
from .observability.metrics import Metrics
from .rag.service import KnowledgeStore
from .tasks.store import TaskStore
from .tools.registry import ToolDenied, ToolExecutionError, ToolRegistry
from .workflow.store import WorkflowStore


class RegistrationRequest(BaseModel):
    email: str
    password: str
    organization_id: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ProjectRequest(BaseModel):
    name: str
    repository: str


class TaskRequest(BaseModel):
    title: str
    workspace: str = "workspace"
    model: str = "mock/mock"


class TaskTransition(BaseModel):
    status: str


class DocumentRequest(BaseModel):
    source: str
    content: str
    chunk_size: int = 800
    chunk_overlap: int = 100


class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    threshold: float = 0.0


class WorkflowRequest(BaseModel):
    name: str
    steps: list[dict[str, object]]


class ApprovalRequest(BaseModel):
    step_id: str
    decision: str


def create_app(
    client: AgentServerClient | None = None,
    auth: AuthService | None = None,
    tasks: TaskStore | None = None,
    tools: ToolRegistry | None = None,
    knowledge: KnowledgeStore | None = None,
    workflows: WorkflowStore | None = None,
    metrics: Metrics | None = None,
    benchmarks: BenchmarkStore | None = None,
) -> FastAPI:
    app = FastAPI(title="Enterprise AI Engineering Agent")
    gateway = client or AgentServerClient(
        os.getenv("AGENT_SERVER_URL", "http://127.0.0.1:8010"),
        os.getenv("AGENT_SERVER_SESSION_API_KEY", "local-only"),
    )
    auth_service = auth
    if auth_service is None and os.getenv("AUTH_SIGNING_KEY"):
        auth_service = AuthService(
            os.getenv("AUTH_DB_PATH", "enterprise-agent-auth.sqlite"),
            os.environ["AUTH_SIGNING_KEY"],
        )
    task_store = tasks or TaskStore(
        os.getenv("TASK_DB_PATH", "enterprise-agent-tasks.sqlite")
    )
    tool_registry = tools or ToolRegistry()
    knowledge_store = knowledge or KnowledgeStore(
        os.getenv("KNOWLEDGE_DB_PATH", "enterprise-agent-knowledge.sqlite")
    )
    workflow_store = workflows or WorkflowStore(
        os.getenv("WORKFLOW_DB_PATH", "enterprise-agent-workflows.sqlite")
    )
    app_metrics = metrics or Metrics()
    benchmark_store = benchmarks or BenchmarkStore(
        os.getenv("BENCHMARK_DB_PATH", "enterprise-agent-benchmarks.sqlite")
    )

    @app.get("/api/v1/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/agent/server-info")
    async def server_info() -> dict[str, object]:
        return await gateway.server_info()

    @app.post("/api/v1/agent/runs")
    async def create_run(request: CreateAgentRun):
        return await gateway.create_run(request)

    @app.post("/api/v1/auth/register")
    async def register(request: RegistrationRequest) -> dict[str, str]:
        if auth_service is None:
            raise HTTPException(
                status_code=503, detail="authentication is not configured"
            )
        try:
            return {
                "user_id": auth_service.register(
                    request.email, request.password, request.organization_id
                )
            }
        except AuthError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/v1/auth/login")
    async def login(request: LoginRequest) -> dict[str, str]:
        if auth_service is None:
            raise HTTPException(
                status_code=503, detail="authentication is not configured"
            )
        try:
            access, refresh = auth_service.login_with_refresh(
                request.email, request.password
            )
            return {"access_token": access, "refresh_token": refresh}
        except AuthError as exc:
            raise HTTPException(status_code=401, detail="invalid credentials") from exc

    @app.post("/api/v1/auth/refresh")
    async def refresh(request: RefreshRequest) -> dict[str, str]:
        if auth_service is None:
            raise HTTPException(
                status_code=503, detail="authentication is not configured"
            )
        try:
            access, refresh_token = auth_service.refresh(request.refresh_token)
            return {"access_token": access, "refresh_token": refresh_token}
        except AuthError as exc:
            raise HTTPException(
                status_code=401, detail="invalid refresh token"
            ) from exc

    @app.post("/api/v1/auth/revoke")
    async def revoke(request: RefreshRequest) -> dict[str, bool]:
        if auth_service is None:
            raise HTTPException(
                status_code=503, detail="authentication is not configured"
            )
        auth_service.revoke(request.refresh_token)
        return {"revoked": True}

    @app.get("/api/v1/auth/me")
    async def me(authorization: str = Header(default="")) -> dict[str, str]:
        if auth_service is None:
            raise HTTPException(
                status_code=503, detail="authentication is not configured"
            )
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing bearer token")
        try:
            return auth_service.verify(authorization.removeprefix("Bearer "))
        except AuthError as exc:
            raise HTTPException(status_code=401, detail="invalid token") from exc

    def claims_from_header(authorization: str) -> dict[str, str]:
        if not authorization.startswith("Bearer ") or auth_service is None:
            raise HTTPException(status_code=401, detail="missing bearer token")
        try:
            return auth_service.verify(authorization.removeprefix("Bearer "))
        except AuthError as exc:
            raise HTTPException(status_code=401, detail="invalid token") from exc

    @app.post("/api/v1/projects")
    async def create_project(
        request: ProjectRequest, authorization: str = Header(default="")
    ) -> dict[str, str]:
        claims = claims_from_header(authorization)
        return {
            "id": auth_service.create_project(claims, request.name, request.repository)
        }

    @app.get("/api/v1/projects")
    async def list_projects(
        authorization: str = Header(default=""),
    ) -> list[dict[str, str]]:
        return auth_service.list_projects(claims_from_header(authorization))

    @app.post("/api/v1/tasks")
    async def create_task(
        request: TaskRequest, authorization: str = Header(default="")
    ) -> dict[str, str]:
        claims = claims_from_header(authorization)
        task = task_store.create(claims["org"], request.title)
        try:
            handle = await gateway.create_run(
                CreateAgentRun(workspace=request.workspace, model=request.model)
            )
            return task_store.attach_conversation(
                task["id"], claims["org"], str(handle.openhands_id)
            )
        except Exception:
            task_store.transition(task["id"], claims["org"], "cancelled")
            raise

    @app.get("/api/v1/tasks")
    async def list_tasks(
        authorization: str = Header(default=""),
    ) -> list[dict[str, str]]:
        return task_store.list(claims_from_header(authorization)["org"])

    @app.get("/api/v1/tasks/{task_id}")
    async def get_task(
        task_id: str, authorization: str = Header(default="")
    ) -> dict[str, str]:
        try:
            return task_store.get(task_id, claims_from_header(authorization)["org"])
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="task not found") from exc

    @app.post("/api/v1/tasks/{task_id}/transition")
    async def transition_task(
        task_id: str,
        request: TaskTransition,
        authorization: str = Header(default=""),
    ) -> dict[str, str]:
        claims = claims_from_header(authorization)
        try:
            task = task_store.get(task_id, claims["org"])
            if request.status == "cancelled" and task["conversation_id"]:
                await gateway.interrupt(UUID(task["conversation_id"]))
            return task_store.transition(task_id, claims["org"], request.status)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="task not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/api/v1/tools")
    async def list_tools(
        authorization: str = Header(default=""),
    ) -> list[dict[str, object]]:
        claims_from_header(authorization)
        return tool_registry.schemas()

    @app.post("/api/v1/tools/{name}/execute")
    async def execute_tool(
        name: str,
        arguments: dict[str, object],
        authorization: str = Header(default=""),
    ) -> dict[str, object]:
        claims = claims_from_header(authorization)
        permissions = (
            {"tool.read"}
            if claims["role"] == "member"
            else {"tool.read", "tool.execute"}
        )
        try:
            return {"result": await tool_registry.execute(name, arguments, permissions)}
        except ToolDenied as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ToolExecutionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/v1/knowledge/documents")
    async def ingest_document(
        request: DocumentRequest, authorization: str = Header(default="")
    ) -> dict[str, str]:
        tenant = claims_from_header(authorization)["org"]
        try:
            document_id = knowledge_store.ingest(
                tenant,
                request.source,
                request.content,
                size=request.chunk_size,
                overlap=request.chunk_overlap,
            )
            return {"document_id": document_id, "status": "ready"}
        except (UnicodeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/v1/knowledge/documents")
    async def list_documents(
        authorization: str = Header(default=""),
    ) -> list[object]:
        return knowledge_store.list_documents(claims_from_header(authorization)["org"])

    @app.delete("/api/v1/knowledge/documents/{document_id}")
    async def delete_document(
        document_id: str, authorization: str = Header(default="")
    ) -> dict[str, bool]:
        try:
            knowledge_store.delete(
                claims_from_header(authorization)["org"], document_id
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="document not found") from exc
        return {"deleted": True}

    @app.post("/api/v1/knowledge/search")
    async def search_knowledge(
        request: SearchRequest, authorization: str = Header(default="")
    ) -> list[object]:
        return knowledge_store.search(
            claims_from_header(authorization)["org"],
            request.query,
            request.limit,
            request.threshold,
        )

    @app.post("/api/v1/knowledge/answer")
    async def answer_from_knowledge(
        request: SearchRequest, authorization: str = Header(default="")
    ) -> dict[str, object]:
        results = knowledge_store.search(
            claims_from_header(authorization)["org"],
            request.query,
            request.limit,
            request.threshold,
        )
        if not results:
            return {
                "answer": "No relevant knowledge-base evidence found.",
                "citations": [],
            }
        citations = [
            {
                "source": item.source,
                "document_id": item.document_id,
                "chunk_id": item.id,
                "page": item.page,
            }
            for item in results
        ]
        context = "\n".join(item.text for item in results)
        return {
            "answer": f"Evidence-backed context:\n{context}",
            "citations": citations,
        }

    @app.post("/api/v1/workflows")
    async def create_workflow(
        request: WorkflowRequest, authorization: str = Header(default="")
    ) -> dict[str, str]:
        try:
            workflow_id = workflow_store.create(
                claims_from_header(authorization)["org"], request.name, request.steps
            )
            return {"id": workflow_id, "status": "queued"}
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/v1/workflows/{workflow_id}")
    async def get_workflow(
        workflow_id: str, authorization: str = Header(default="")
    ) -> dict[str, object]:
        try:
            return workflow_store.get(
                claims_from_header(authorization)["org"], workflow_id
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="workflow not found") from exc

    @app.get("/api/v1/workflows")
    async def list_workflows(
        authorization: str = Header(default=""),
    ) -> list[dict[str, object]]:
        return workflow_store.list(claims_from_header(authorization)["org"])

    @app.get("/api/v1/workflows/{workflow_id}/ready")
    async def ready_workflow_steps(
        workflow_id: str, authorization: str = Header(default="")
    ) -> list[dict[str, object]]:
        try:
            return workflow_store.ready_steps(
                claims_from_header(authorization)["org"], workflow_id
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="workflow not found") from exc

    @app.post("/api/v1/workflows/{workflow_id}/approve")
    async def approve_workflow_step(
        workflow_id: str,
        request: ApprovalRequest,
        authorization: str = Header(default=""),
    ) -> dict[str, bool]:
        claims = claims_from_header(authorization)
        if claims["role"] not in {"admin", "owner"}:
            raise HTTPException(status_code=403, detail="approval role required")
        try:
            workflow_store.approve(
                claims["org"],
                workflow_id,
                request.step_id,
                claims["sub"],
                request.decision,
            )
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"accepted": True}

    @app.get("/api/v1/workflows/{workflow_id}/history")
    async def workflow_history(
        workflow_id: str, authorization: str = Header(default="")
    ) -> list[dict[str, object]]:
        try:
            return workflow_store.history(
                claims_from_header(authorization)["org"], workflow_id
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="workflow not found") from exc

    @app.get("/api/v1/metrics/summary")
    async def metrics_summary(
        authorization: str = Header(default=""),
    ) -> dict[str, object]:
        claims = claims_from_header(authorization)
        task_items = task_store.list(claims["org"])
        counts = {
            status: sum(item["status"] == status for item in task_items)
            for status in {item["status"] for item in task_items}
        }
        return {
            "tenant": claims["org"],
            "tasks": counts,
            "metrics": app_metrics.snapshot().__dict__,
        }

    @app.get("/api/v1/metrics/agent")
    async def agent_metrics(
        authorization: str = Header(default=""),
    ) -> dict[str, object]:
        return await metrics_summary(authorization)

    @app.get("/api/v1/metrics/tools")
    async def tool_metrics(
        authorization: str = Header(default=""),
    ) -> dict[str, object]:
        claims_from_header(authorization)
        return {"metrics": app_metrics.snapshot().counters}

    @app.get("/api/v1/benchmarks")
    async def list_benchmarks(
        authorization: str = Header(default=""),
    ) -> list[dict[str, object]]:
        return benchmark_store.list(claims_from_header(authorization)["org"])

    @app.post("/api/v1/benchmarks/run")
    async def run_benchmark(
        authorization: str = Header(default=""),
    ) -> dict[str, object]:
        tenant = claims_from_header(authorization)["org"]
        result = retrieval_scores(
            [RetrievalCase("synthetic", {"synthetic-doc"})], [["synthetic-doc"]], 1
        )
        run_id = benchmark_store.save(tenant, "rag-retrieval", "deterministic", result)
        return {
            "id": run_id,
            "kind": "rag-retrieval",
            "mode": "deterministic",
            "result": result,
        }

    return app


app = create_app()
