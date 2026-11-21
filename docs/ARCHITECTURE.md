# Enterprise AI Engineering Agent — Architecture

状态：Stage 7 前后端增量实现中  
上游基线：OpenHands Software Agent SDK 1.54.0

## 1. 架构原则

1. **业务层与 Agent 执行层隔离**：业务数据库不依赖 OpenHands 私有状态结构。
2. **上游只通过公共 API 接入**：优先 REST/WebSocket 和 `openhands.sdk` 公共导出。
3. **默认最小权限**：工具、项目、文档、GitHub、网络和沙箱权限显式授予。
4. **事件驱动但不共享事务**：OpenHands event 与业务 event 通过映射表关联。
5. **可恢复优先**：所有长任务具有状态、attempt、timeout、retry 和审批点。
6. **简单任务不强制多 Agent**：Router 根据复杂度和风险选择执行策略。
7. **真实能力与 Mock 严格区分**：测试和 UI 都记录验证等级。
8. **公开仓库安全默认值**：配置模板不含真实身份或私有路径。

## 2. 系统边界

```text
┌──────────────────────────────────────────────────────────────┐
│ React + TypeScript Web                                      │
│ Project / Task / Run / Knowledge / Approval / Evaluation UI │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTPS / Business WebSocket
┌──────────────────────▼───────────────────────────────────────┐
│ Platform API (FastAPI)                                      │
│ Auth · RBAC · Projects · Tasks · Runs · Audit · GitHub      │
└───────────┬───────────────┬───────────────────┬──────────────┘
            │               │                   │
┌───────────▼──────┐ ┌──────▼────────┐ ┌────────▼─────────────┐
│ PostgreSQL       │ │ Workflow      │ │ RAG Service          │
│ pgvector         │ │ Orchestrator  │ │ Parse/Index/Retrieve │
└──────────────────┘ └──────┬────────┘ └──────────────────────┘
                            │ AgentRun contract
                  ┌─────────▼──────────────────────────────┐
                  │ Agent Gateway / OpenHands Adapter     │
                  │ policy · event mapping · version gate │
                  └─────────┬──────────────────────────────┘
                            │ REST / WebSocket
                  ┌─────────▼──────────────────────────────┐
                  │ OpenHands Agent Server 1.54.0         │
                  │ Agent · Tools · MCP · Conversation    │
                  └─────────┬──────────────────────────────┘
                            │
                  ┌─────────▼──────────────────────────────┐
                  │ Docker Sandbox / Remote Workspace     │
                  │ repo checkout · commands · tests      │
                  └────────────────────────────────────────┘
```

## 3. 建议目录

```text
Enterprise-AI-Engineering-Agent/
├── backend/
│   ├── app/
│   │   ├── api/                 # HTTP/WebSocket controllers
│   │   ├── application/         # use cases and transaction boundaries
│   │   ├── domain/              # entities, policies, domain events
│   │   ├── infrastructure/      # DB, GitHub, object store, queues
│   │   ├── auth/                # JWT, password, RBAC
│   │   ├── agent_gateway/       # OpenHands anti-corruption layer
│   │   ├── workflow/            # durable orchestration
│   │   ├── rag/                 # ingestion and retrieval
│   │   ├── evaluation/          # benchmark execution and metrics
│   │   ├── observability/       # traces, metrics, audit events
│   │   └── config/              # typed settings
│   ├── migrations/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── features/
│   │   ├── entities/
│   │   ├── shared/
│   │   └── generated/           # generated business API client
│   └── tests/
├── agent_profiles/              # planner/code/test/review definitions
├── mcp_servers/                 # project-owned MCP servers only
├── sandbox/                     # Dockerfiles and security policies
├── benchmarks/                  # public, synthetic, reproducible tasks
├── deploy/                      # compose; later optional k8s
├── scripts/                     # deterministic maintenance scripts
├── docs/
├── tests/                       # cross-service/E2E tests
├── .env.example
├── .gitignore
├── LICENSE
├── NOTICE
└── README.md
```

目录不会复制 `openhands-sdk` 或 `OpenHands-main`。开发环境可通过固定 wheel/tag、固定镜像和 sibling source override 三种方式切换，但 CI 只允许可复现的固定版本。

## 4. 核心领域模型

### 4.1 身份与权限

- `User`
- `Organization`
- `Membership`
- `Role`
- `Permission`
- `ApiCredentialReference`

JWT access token 短时有效，refresh token 只保存哈希并支持 rotation/revocation。凭据值不进入 PostgreSQL 普通字段和日志。

### 4.2 项目与任务

- `Project`：组织、仓库、默认分支、策略。
- `Task`：用户目标和业务状态。
- `AgentRun`：一次可恢复执行。
- `RunAttempt`：某次实际调度尝试。
- `ApprovalRequest`：待审批风险动作。
- `Artifact`：补丁、测试日志、报告、引用。
- `AuditEvent`：不可变的业务审计记录。

### 4.3 OpenHands 映射

```text
AgentRun.id                本项目稳定 ID
AgentRun.openhands_id      OpenHands conversation ID
RunEvent.external_event_id OpenHands event ID
RunAttempt.workspace_id    sandbox/runtime ID
```

业务状态不直接等于 OpenHands execution status。Adapter 负责把 OpenHands 状态映射为本项目状态机，未知状态必须进入 `needs_attention`，不能静默当成功。

## 5. Agent Gateway

Agent Gateway 是最重要的兼容层，只向业务代码暴露以下稳定协议：

```python
class AgentRuntime(Protocol):
    async def create_run(self, request: CreateAgentRun) -> RuntimeHandle: ...
    async def send_message(self, run_id: UUID, message: UserMessage) -> None: ...
    async def start(self, run_id: UUID) -> None: ...
    async def pause(self, run_id: UUID) -> None: ...
    async def interrupt(self, run_id: UUID) -> None: ...
    async def approve(self, run_id: UUID, decision: ApprovalDecision) -> None: ...
    async def stream_events(self, run_id: UUID) -> AsyncIterator[RuntimeEvent]: ...
```

初始实现使用 Agent Server REST/WebSocket，不直接调用 `ConversationService`、`EventService` 等私有服务类。Standalone SDK 只用于单元级实验和离线 runner，不作为生产业务 API 进程中的默认模式。

Gateway 职责：

- Agent Server 版本探测。
- 请求/事件 schema 转换。
- OpenHands ID 与业务 ID 关联。
- 重连、去重和 event cursor。
- 安全事件映射。
- observability metadata 注入。
- contract tests。

## 6. Agent 设计

### 6.1 路由策略

```text
Task Intake
  → policy/risk classification
  → simple task: Code Agent
  → complex task: Planner → parallel specialists → Aggregator
  → high-risk task: approval before write/network/GitHub action
```

### 6.2 角色

- **Planner Agent**：只读分析、分解、依赖和验收标准。
- **Code Agent**：在隔离 workspace 修改代码。
- **Research Agent**：知识库和经批准的外部信息检索。
- **Test Agent**：运行允许的测试并归类失败。
- **Review Agent**：独立检查补丁、安全、兼容性和证据。
- **Result Aggregator**：只汇总真实事件和 artifact，不虚构成功。

Agent profiles 使用声明式配置，不在业务代码中散落 prompt。每次运行记录 profile version、model、tool policy 和 prompt hash。

## 7. Workflow 状态机

```text
queued → planning → running → awaiting_approval → running
   │          │          │              │
   ├─ cancelled          ├─ retrying     └─ rejected
   └─ failed             ├─ paused
                         └─ succeeded / failed / needs_attention
```

核心要求：

- step 具有唯一 ID 和幂等 key。
- attempt 独立计数。
- timeout 和 retry policy 持久化。
- 并行 fan-out/fan-in 有并发配额。
- 人工审批是可恢复状态，而非阻塞进程。
- 服务重启后从数据库恢复未完成任务。
- OpenHands Conversation 只负责 Agent 执行，业务 orchestrator 负责 durable lifecycle。

第一版可实现数据库驱动的轻量 orchestrator；达到多实例和高可靠要求后再评估 Temporal。不能一开始同时引入 Celery、Temporal 和自研队列。

## 8. RAG 架构

```text
Upload/Repository Sync
  → MIME/type validation
  → parser (PDF/DOCX/TXT/MD/source)
  → normalized document
  → structure-aware chunks
  → embedding + tsvector
  → PostgreSQL/pgvector

Query
  → ACL filter
  → vector retrieval + BM25
  → fusion
  → optional reranker
  → citation builder
  → Agent context/tool response
```

每个 chunk 必须携带 organization、project、document、revision、source locator 和 content hash。检索前先应用权限过滤，不能先召回后删除敏感结果。

Embedding、reranker 和生成模型均通过接口抽象，允许本地和云端实现。阶段初期使用小规模公开/合成文档，不下载大型数据集。

## 9. Tool 与 MCP 权限模型

每次工具调用执行前计算：

```text
effective permission = user role
                     ∩ project policy
                     ∩ agent profile policy
                     ∩ run policy
                     ∩ sandbox capability
```

工具风险级别：

- `read`：读取项目允许范围。
- `write`：修改沙箱文件，需要 run policy 允许。
- `execute`：执行命令，受 allow/deny policy 和资源限制。
- `network`：外部网络访问，默认关闭。
- `external_write`：GitHub、数据库或第三方写入，必须人工审批。

MCP server 分为内置、组织批准和用户临时三类。配置只保存 secret reference，不保存明文 token。

## 10. Sandbox

最低安全基线：

- 每个 run 独立容器或等价隔离单元。
- 非 root 用户。
- 只挂载该任务 workspace。
- CPU、内存、进程数、磁盘和执行时间限制。
- 默认无 Docker socket。
- 默认禁止特权模式。
- 默认无外部网络；按域名或代理策略开放。
- artifact 通过受控出口导出。
- 容器退出后清理，保留策略由业务数据库记录。
- 高风险命令进入 approval。

Windows 主机建议使用 WSL2 + Docker Desktop；不以原生 Windows Agent Server 为生产目标。

## 11. API 与前端

业务 API 采用 `/api/v1`，与 OpenHands `/api` 分离。主要资源：

- `/auth`
- `/organizations`
- `/projects`
- `/tasks`
- `/runs`
- `/runs/{id}/events`
- `/runs/{id}/approvals`
- `/knowledge-bases`
- `/documents`
- `/evaluations`
- `/audit-events`
- `/integrations/github`

前端按 feature slice 组织，不直接复刻 Agent Canvas。首要页面：

1. 项目与仓库。
2. 任务创建。
3. Run timeline。
4. 计划和子 Agent 拓扑。
5. 工具调用与审批。
6. Patch/test/artifact。
7. Knowledge documents。
8. Evaluation dashboard。

## 12. 数据与秘密信息

- `.env` 永不提交，只提交 `.env.example`。
- secret 值由环境变量或 secret manager 提供。
- 数据库仅保存 opaque secret reference。
- 日志默认结构化并经过字段级脱敏。
- 用户上传内容不进入普通 debug 日志。
- benchmark 使用公开或合成数据。
- artifact 设置 TTL 和删除策略。
- GitHub token 使用最小 scope，默认 read-only。

## 13. 测试架构

| 层级 | 范围 |
| --- | --- |
| Unit | domain policy、mapping、parser、retrieval fusion |
| API | auth、RBAC、validation、error contract |
| DB integration | PostgreSQL、migration、tenant isolation |
| Runtime contract | 固定 Agent Server 1.54.0 的 REST/WebSocket |
| Sandbox integration | 真实容器、资源和文件隔离 |
| Model live | 明确标记且需用户授权的真实模型测试 |
| E2E | 浏览器到 Agent artifact 的完整路径 |
| Security | IDOR、JWT、secret redaction、path traversal、command approval |

每份测试报告记录 `mock`、`local-real`、`integration` 或 `unverified`，禁止把 Mock 当作真实运行证据。

## 14. 发布架构决策

- 第一版发布使用 Docker Compose：API、worker、PostgreSQL/pgvector、frontend、Agent Server。
- 不在第一阶段引入 Kubernetes。
- GitHub PR 仅创建草稿，默认不 merge。
- 发布前执行 secret scan、license scan、tracked files scan、history scan、image config scan 和 artifact scan。
- 未经用户明确批准，不初始化远程仓库、不 push、不创建 GitHub 资源。
