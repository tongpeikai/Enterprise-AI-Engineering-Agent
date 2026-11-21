# Enterprise AI Engineering Agent — Development Plan

状态：待用户验收  
执行规则：每阶段实现、测试、修复、复测、更新文档、提交验收清单，然后等待用户确认

## 1. 前置约束

本计划不会：

- 修改或删除 `software-agent-sdk-main`、`OpenHands-main`、`OpenHands-CodeTask-Agent`。
- 未经许可安装大型依赖、下载模型/数据集或调用付费 API。
- 未经许可执行 commit、push、GitHub 写操作或公开发布。
- 用 Mock 结果宣称真实模型、容器、数据库或外部服务已验证。

## 2. 阶段总览

| 阶段 | 内容 | 预计时间 | 新增磁盘估计 |
| --- | --- | ---: | ---: |
| 0 | 可追溯源码与环境基线 | 3–5 天 | 5–12 GB，不含模型 |
| 1 | 独立项目骨架、安全基线、CI | 4–6 天 | 1–3 GB |
| 2 | 业务 API、Auth、RBAC、PostgreSQL | 2–3 周 | 2–5 GB |
| 3 | OpenHands Agent Gateway 与真实执行 | 2–3 周 | 5–15 GB 镜像/工作区 |
| 4 | 前端控制台与实时事件 | 2–3 周 | 1–3 GB |
| 5 | RAG、pgvector、BM25、权限 | 3–4 周 | 3–15 GB，随语料增长 |
| 6 | Multi-Agent 与 durable workflow | 3–4 周 | 1–3 GB |
| 7 | Sandbox 安全加固 | 2–3 周 | 5–15 GB 镜像 |
| 8 | Benchmark 与可观测性 | 2–3 周 | 2–10 GB |
| 9 | GitHub 自动化（默认只读） | 2–3 周 | 取决于测试仓库 |
| 10 | 发布审计与公开准备 | 1–2 周 | 小于 2 GB |

单人连续开发估计 20–32 周；可展示的纵向 MVP 约 6–9 周。估计不包含等待外部服务、用户审批和大型模型实验时间。

当前 D 盘约剩余 134.1 GB，足够完成不含大型模型的开发，但 Docker 镜像、多个测试仓库、数据库卷和模型缓存必须设置清理与配额。RTX 5080 16 GB 不代表磁盘充足，任何模型下载仍需单独审批。

## 3. 立即下一阶段：Stage 0

### 3.1 目标

建立可追溯、可复现、不会污染上游源码的开发基线。

### 3.2 工作项

1. 经用户批准后，为新项目初始化本地 Git；不配置 remote、不 commit。
2. 从官方来源重新获取或验证 SDK 1.54.0 的 tag/commit；若需要下载，先确认体积和来源。
3. 记录上游 commit、package hashes、Agent Server image digest。
4. 配置 WSL2 Ubuntu 作为后端开发环境。
5. 配置 uv/Python 3.13。
6. 配置 Docker Desktop 与 WSL integration。
7. 配置 PostgreSQL + pgvector 容器。
8. 配置 Node 24/npm。
9. 运行固定的 SDK smoke tests。
10. 运行 Agent Server health/server_info。
11. 运行 REST/WebSocket contract smoke test。
12. 只使用 Mock LLM 验证无费用路径。
13. 若用户允许，再选择 Ollama 现有模型或云模型进行真实工具调用测试。

### 3.3 需要用户提前批准的事项

- 安装/启用 WSL2。
- 安装 Docker Desktop 或其他 Docker Engine。
- 安装 PostgreSQL 客户端（若使用容器可不装本机 server）。
- 安装项目 Python/npm 依赖。
- 下载任何 Agent Server/Docker 镜像。
- 下载任何 Ollama 模型。
- 调用任何付费模型。
- 初始化本地 Git、commit 或连接 remote。

### 3.4 Stage 0 验收标准

- [ ] 新项目与三个既有目录完全隔离。
- [ ] 上游 SDK commit/tag 可追溯。
- [ ] Python、Node、uv、Docker 版本写入环境报告。
- [ ] `docker compose config` 通过。
- [ ] PostgreSQL 和 pgvector health 通过。
- [ ] Agent Server `/alive`、`/ready`、`/server_info` 通过。
- [ ] REST 创建会话和 WebSocket 连接通过 Mock LLM 验证。
- [ ] 没有真实 secret 写入项目文件。
- [ ] Stage 0 测试日志和失败项归档。
- [ ] 所有能力标注验证等级。

## 4. Stage 1：项目骨架与安全基线

### 内容

- 建立 backend/frontend/deploy/sandbox/benchmarks/docs。
- 根 README、MIT License、NOTICE、CONTRIBUTIONS、CHANGELOG。
- `.gitignore`、`.dockerignore`、`.env.example`。
- Typed settings，启动时强校验。
- Ruff/Pyright/Pytest、ESLint/Prettier/Vitest。
- pre-commit，包括 secret scanning 和大文件检查。
- CI 只运行无外部费用的检查。
- 第三方许可证清单。

### 验收

- [ ] 空骨架可启动但不伪造业务能力。
- [ ] Backend/Frontend lint、typecheck、unit tests 通过。
- [ ] `.env.example` 只有虚构占位符。
- [ ] secret scan 对测试密钥 fixture 能正确报警。
- [ ] 未跟踪运行缓存、数据库、上传或日志。
- [ ] 上游 attribution 明确。

## 5. Stage 2：业务系统与数据库

### 内容

- FastAPI `/api/v1`。
- SQLAlchemy 2.x async。
- Alembic migrations。
- PostgreSQL。
- User、Organization、Membership、Role、Project、Task、AgentRun、Approval、Artifact、AuditEvent。
- JWT access/refresh rotation。
- password hashing。
- RBAC 和 tenant filters。
- API error envelope 和 pagination。

### 验收

- [ ] migration 从空库升级和降级测试。
- [ ] 两组织之间 IDOR/数据隔离测试。
- [ ] token rotation/revocation 测试。
- [ ] audit event 不包含 secret。
- [ ] API contract 自动生成。

## 6. Stage 3：Agent Gateway

### 内容

- 固定 OpenHands Server 1.54.0。
- REST/WebSocket adapter。
- 状态和事件规范化。
- event cursor、重连、去重。
- run/attempt 持久化。
- start/pause/interrupt/approve。
- 真实 Terminal 和只读文件工具验证。
- tool policy 和审批前置。

### 验收

- [ ] Mock LLM contract tests。
- [ ] 本地真实 Agent Server 集成测试。
- [ ] 至少一次真实工具调用并保存原始事件证据。
- [ ] 服务重启后 run 状态可以恢复。
- [ ] 未授权 write/execute 被拒绝。
- [ ] 上游错误不会被错误标记为成功。

## 7. Stage 4：前端

### 内容

- React + TypeScript。
- 登录、项目、任务、Run timeline。
- WebSocket reconnect。
- Plan/subagent/tool/approval/artifact UI。
- API client 由本项目 OpenAPI 生成。

### 验收

- [ ] 关键页面 component tests。
- [ ] WebSocket 断线重连测试。
- [ ] RBAC UI 与后端授权一致。
- [ ] Playwright 完整任务路径。
- [ ] 浏览器不保存高权限密钥。

## 8. Stage 5：RAG

### 内容

- PDF、DOCX、TXT、Markdown、源码 parser。
- 大小、MIME、zip bomb 和路径安全检查。
- structure-aware chunking。
- pgvector + PostgreSQL full-text search。
- reciprocal rank fusion。
- 可插拔 reranker。
- 引用和 source locator。
- 文档 ACL、revision、delete/reindex。

### 验收

- [ ] 每种文档类型有真实本地 fixture。
- [ ] ACL 在查询阶段生效。
- [ ] 删除后 chunk/vector 全部清理。
- [ ] 固定公开/合成语料的 Recall@K 报告。
- [ ] 引用能定位到原始文档片段。
- [ ] 未验证 reranker 不写为已完成。

## 9. Stage 6：Multi-Agent 与 Workflow

### 内容

- Planner、Code、Research、Test、Review、Aggregator profiles。
- task router。
- 顺序、并行、依赖和 fan-in。
- timeout/retry/cancel。
- durable approval。
- 失败恢复和结果证据验证。

### 验收

- [ ] 简单任务走单 Agent。
- [ ] 复杂任务有可追踪 DAG。
- [ ] 并行上限生效。
- [ ] 单个子 Agent 失败不导致结果伪造。
- [ ] 进程重启后能恢复 waiting/retry 状态。
- [ ] Aggregator 只引用已保存 artifact/event。

## 10. Stage 7：Sandbox

### 内容

- 非 root image。
- per-run workspace。
- CPU/RAM/PID/disk/time limits。
- no privileged、no Docker socket。
- network default deny。
- artifact controlled export。
- lifecycle cleanup 和 TTL。

### 验收

- [ ] 容器不能读取宿主非挂载文件。
- [ ] 跨 run 文件不可见。
- [ ] 资源超限会终止并记录原因。
- [ ] 未批准外网访问失败。
- [ ] dangerous command 进入审批。
- [ ] cleanup 后无孤儿容器和敏感卷。

## 11. Stage 8：Benchmark 与可观测性

### 指标

- Task Success Rate。
- Tool Success Rate。
- Retrieval Recall@K / MRR。
- Answer Correctness。
- Latency P50/P95。
- Token Usage。
- Cost per Task。
- Recovery Rate。
- Approval Rate 和拒绝后安全结果。

### 验收

- [ ] benchmark tasks 固定版本且公开可发布。
- [ ] 报告含运行环境、模型、prompt/profile hash。
- [ ] Mock 与 live 分开统计。
- [ ] 失败样本保留错误分类。
- [ ] 指标由原始事件计算，不手工填写。

## 12. Stage 9：GitHub 自动化

### 内容

- GitHub App 或 fine-grained token。
- repository/issue/PR 只读同步。
- sandbox clone。
- issue analysis、patch、tests、review。
- 独立分支和 PR draft payload。
- external write approval。

### 验收

- [ ] 默认 read-only。
- [ ] 没有用户明确批准不执行写操作。
- [ ] token scope 最小化。
- [ ] 测试仓库与真实重要仓库分离。
- [ ] 不自动 merge 默认分支。
- [ ] PR 草稿包含真实测试证据和未验证项。

## 13. Stage 10：发布准备

### 必须通过

- 全量测试和失败说明。
- secret scan：工作树、tracked files、staging、history。
- 许可证和 NOTICE。
- README、截图和文档隐私检查。
- Docker build context 检查。
- 测试数据和 artifacts 检查。
- SBOM 和依赖漏洞报告。
- 一键部署复测。
- 最终发布审计报告。

任何真实密钥或私人数据命中都立即停止发布。未经用户明确批准，不创建公开仓库、不 push、不发布镜像。

## 14. 文档交付计划

| 文档 | 首次建立阶段 |
| --- | --- |
| `README.md` | Stage 1 |
| `docs/BASELINE_AUDIT.md` | 已完成 |
| `docs/ARCHITECTURE.md` | 已完成 |
| `docs/DEVELOPMENT_PLAN.md` | 已完成 |
| `docs/API.md` | Stage 2 |
| `docs/DATABASE.md` | Stage 2 |
| `docs/AGENT_DESIGN.md` | Stage 3/6 |
| `docs/RAG_DESIGN.md` | Stage 5 |
| `docs/SECURITY.md` | Stage 1，持续维护 |
| `docs/TESTING.md` | Stage 1，持续维护 |
| `docs/DEPLOYMENT.md` | Stage 0/7 |
| `docs/CONTRIBUTIONS.md` | Stage 1 |
| `docs/CHANGELOG.md` | Stage 1，持续维护 |

## 15. 第一阶段启动决策点

用户验收本轮文档后，需要选择并明确批准：

1. 是否允许初始化新项目的本地 Git 仓库（不 commit、不配置 remote）。
2. 是否允许启用/安装 WSL2。
3. 是否允许安装 Docker Desktop。
4. 是否允许下载固定 Agent Server 和 PostgreSQL/pgvector 镜像。
5. 是否允许安装新项目的 Python/npm 依赖。
6. 是否允许使用本机已有 Ollama 模型；若模型不存在，下载必须另行批准。

在这些决定之前，不进入正式实现。
