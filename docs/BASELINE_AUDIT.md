# Enterprise AI Engineering Agent — Baseline Audit

审计日期：2026-11-20  
审计范围：`software-agent-sdk-main`、`OpenHands-main`、本机开发环境  
审计性质：只读源码审计；未安装依赖、未下载模型、未启动服务、未调用付费 API

## 1. 结论摘要

当前打开的仓库是 OpenHands Software Agent SDK 源码快照，路径为：

`<workspace>/software-agent-sdk-main`

它不是 Agent Canvas 主项目，也不是 Git 工作树。目录没有 `.git`，所以无法从本地验证 commit SHA、分支、tag 签名或是否存在未提交修改。源码和包元数据一致声明版本为 `1.54.0`，并声明来源为 `https://github.com/OpenHands/software-agent-sdk`。

相邻的 `OpenHands-main` 是 Agent Canvas 前端源码快照，版本 `1.27.1`。它通过 `@openhands/typescript-client 1.54.0` 消费本仓库提供的 Agent Server API。两个目录均没有 `.git`，因此都只能视为不可追溯的源码快照。

新平台不应直接修改这两个上游目录。独立项目目录确定为：

`<workspace>/Enterprise-AI-Engineering-Agent`

## 2. 验证状态约定

- **已验证**：直接检查了当前文件、源码或本机命令结果。
- **未验证**：当前缺少运行条件，不能声称能力已真实工作。
- **设计判断**：基于已验证源码作出的架构决策，尚待实现验证。

## 3. 上游项目关系

### 3.1 Software Agent SDK

**已验证**：该仓库拥有 Python SDK、Agent Server、Tools、Workspace 和浏览器兼容 TypeScript Client。

版本一致性：

| 组件 | 版本 |
| --- | --- |
| `openhands-sdk` | 1.54.0 |
| `openhands-agent-server` | 1.54.0 |
| `openhands-tools` | 1.54.0 |
| `openhands-workspace` | 1.54.0 |
| `@openhands/typescript-client` | 1.54.0 |
| 固定 Agent Server 镜像 | `ghcr.io/openhands/agent-server:1.54.0-python` |

### 3.2 OpenHands-main / Agent Canvas

**已验证**：`OpenHands-main` 的 npm 包名为 `@openhands/agent-canvas`，版本 1.27.1，依赖 `@openhands/typescript-client 1.54.0`。它负责 UI、前端状态、后端选择和本地栈编排，不是 Python Agent 内核。

调用关系：

```text
software-agent-sdk
  ├─ Python SDK：Agent 行为、工具、事件、会话、状态
  ├─ Agent Server：REST/WebSocket 权威实现
  └─ TypeScript Client：浏览器端类型化客户端
          ↓
OpenHands / Agent Canvas
  └─ UI、前端状态、运行后端选择、本地栈编排
```

### 3.3 版权与许可证

**已验证**：SDK 使用 MIT License，版权声明为 `Copyright (c) 2026 OpenHands contributors`。

新项目必须：

1. 保留上游 LICENSE 和 attribution。
2. 不将 OpenHands 商标或项目名称表述为本项目所有。
3. 在 NOTICE/README 中区分上游依赖与自主代码。
4. 若未来复制任何上游源码，保留原始版权头和许可证。
5. 优先以包依赖和 API 集成代替源码复制。

## 4. 源码规模与结构

| 模块 | 源文件数 | 约代码行数 |
| --- | ---: | ---: |
| Python SDK | 310 | 68,365 |
| Agent Server | 97 | 29,223 |
| Tools | 93 | 14,505 |
| Workspace | 14 | 2,605 |
| TypeScript Client | 109 | 46,770 |
| Python 测试文件 | 641 | 未统计行数 |
| TypeScript 测试文件 | 33 | 未统计行数 |

核心 SDK 子模块包括 `agent`、`conversation`、`event`、`llm`、`context`、`tool`、`workspace`、`mcp`、`skills`、`plugin`、`security`、`hooks`、`subagent`、`settings` 和 `observability`。

## 5. 实际可复用接口

以下结论均来自当前源码，而不是根据目录名称推测。

### 5.1 Python SDK

建议通过 `openhands.sdk` 公共导出面使用：

- `LLM`
- `Agent` / `AgentBase`
- `Conversation` / `LocalConversation` / `RemoteConversation`
- `LocalWorkspace` / `RemoteWorkspace`
- `Tool` / `ToolDefinition` / `register_tool`
- `Event` / `MessageEvent` / `HookExecutionEvent`
- `AgentContext`
- `LLMSummarizingCondenser`
- `MCPClient` / `create_mcp_tools`
- Agent settings、confirmation、security analyzer、skills 和 subagent API

`Conversation` 工厂根据 workspace 类型选择本地或远程会话。LocalConversation 接受本地路径、持久化目录、callbacks、token callbacks、hooks、secrets、tags、client tools 和 observability metadata。RemoteConversation 通过 `/api/conversations` 调用 Agent Server。

### 5.2 Agent Server

已验证的主要 API 家族：

- Conversations：创建、查询、运行、暂停、中断、确认、压缩、分叉、导航。
- Events：分页、搜索、写入、确认响应。
- WebSocket：conversation events、session、bash events。
- Workspace：文件、命令、Git changes/diff/commits。
- Settings、Secrets、Agent Profiles、LLM Profiles。
- MCP、Skills、Plugins、Hooks、Subagents。
- ACP model discovery。
- Docker runtime 与运行时凭据。
- VSCode、Canvas Extensions。
- OpenAI-compatible `/v1/models` 和 completion 路径。
- 健康检查、ready、server_info、deferred init。

### 5.3 TypeScript Client

可直接复用：

- `ConversationManager`
- `RemoteConversation`
- `RemoteWorkspace`
- `RemoteEventsList`
- `HttpClient`
- WebSocket clients
- `MCPClient`
- Agent Server 版本兼容检查
- 自动生成的 OpenAPI transport types

设计上，新前端应通过本项目后端获取业务数据；只有事件流和工作区交互确有收益时，才直接使用 TypeScript Client 连接 Agent Server。浏览器不应持有模型或高权限 Server 密钥。

## 6. 能力审计

### 6.1 Agent 执行

**已验证**：同步/异步 Agent loop、工具调用、事件投影、最大迭代限制、stuck detection、并行工具执行、暂停、中断、恢复和分叉均存在真实实现。

**未验证**：本机没有 LLM API 凭据，本轮没有完成真实模型任务。

### 6.2 模型接入

**已验证**：基于 LiteLLM 1.93.0，存在 Chat/Responses、同步/异步、流式、重试、超时、fallback、usage/cost 和模型能力注册。源码包含 OpenAI、Anthropic、Azure、Bedrock、Vertex、Gemini、OpenRouter、Ollama 和 vLLM 相关路径。

**未验证**：各 provider 的真实连接、费用、吞吐和工具调用质量。

### 6.3 Tools、MCP 和 Skills

**已验证**：终端、文件编辑、Apply Patch、Grep、Glob、Browser、Task Tracker、Planning、Delegate、Workflow、MCP 动态工具和客户端自定义工具均有真实 executor/schema 实现。

**封装要求**：业务平台必须在 OpenHands 工具外增加 `ToolPolicy`，统一处理租户权限、项目权限、风险级别、审批、网络和审计。不能让业务层直接按名称任意启用高权限工具。

### 6.4 Multi-Agent 与 Workflow

**已验证**：Delegate、TaskManager 和动态 Workflow 支持子 Agent、并发 map、pipeline、reduce、超时和失败聚合。

**限制**：这不是跨进程 durable workflow engine。长期任务、可靠重试、人工审批恢复和多实例调度必须由本项目自主开发或接入专用工作流系统。

### 6.5 状态与记忆

**已验证**：ConversationState、EventStore、文件持久化、上下文压缩、MEMORY.md、SOUL.md、Skills progressive disclosure、resume/fork 均存在。

**缺失**：企业知识库、向量检索、权限感知召回、记忆质量评测和结构化业务状态数据库。

### 6.6 安全与恢复

**已验证**：LLM 异常分类、tenacity 重试、流 idle timeout、confirmation policy、security analyzer、secret serializer、cipher、redaction、hooks、工具取消传播均存在。

**必须自主补充**：RBAC、租户隔离、数据保留策略、审计日志、CSRF/CORS 策略、refresh token 轮换、网络出口策略、容器资源限制、GitHub credential scopes 和发布前 secrets scan。

## 7. 持久化与数据库

**已验证**：核心会话、事件、设置和 Secrets 主要使用 LocalFileStore、EventStore 和 JSON 文件存储。Settings/Secrets 使用临时文件替换和文件锁。

`openhands-agent-server` 声明了 SQLAlchemy、Alembic 和 aiosqlite 依赖，但在当前核心源码中未检索到实际 SQLAlchemy engine、session 或 Alembic migration 使用。因此不能声称上游已经提供生产级关系数据库持久化。

**设计结论**：本项目自主使用 PostgreSQL 保存用户、组织、项目、任务、执行索引、审批、审计、RAG metadata 和 evaluation 结果；OpenHands 的原始事件流作为外部执行记录，通过稳定 ID 建立关联，不直接替换上游内部 FileStore。

## 8. Examples 和测试

### 8.1 Examples

- 90 个 Python 示例全部通过 AST 解析。
- 仓库测试发现 80 个示例候选。
- 70 个列为非交互运行候选。
- 10 个明确因交互输入或额外基础设施排除。

当前没有 LLM/GitHub/observability API key，Docker、WSL 和 Kubernetes 不可用，所以未完成真实示例 E2E。

### 8.2 Tests

- 收集 11,966 项。
- 默认选中 11,929 项。
- 37 项因 stress、ACP live、Docker live 等标记排除。
- 4 项收集期跳过。
- 测试树完整收集，无 import error。

原生 Windows 全量运行在约 5% 后出现长时间无输出并被主动中止。定向复现早期失败区域结果：

```text
101 tests
81 passed
20 failed
```

失败集中在 `os.getuid/getgid`、POSIX 权限、signal/process group、symlink/path semantics 和 Windows 上 unsupported 的 Canvas Extension backend。这证明全仓原生 Windows 不是主要支持路径；不能据此断言 Linux CI 回归。

CI 的主 SDK、Agent Server、Workspace 和 Cross 测试在 Ubuntu 上运行。Windows CI 只运行 Tools 子集并明确排除多项 terminal/browser/file-editor 测试。

覆盖率在 CI 中收集，但 Python 使用 `--cov-fail-under=0`，TypeScript 也没有阈值。本地没有覆盖率产物。

## 9. 本机环境

| 项目 | 状态 |
| --- | --- |
| Windows | Windows 11 专业版，build 26200 |
| CPU | Intel Core Ultra 7 270K Plus，24C/24T |
| RAM | 约 25 GB |
| GPU | RTX 5080，16,303 MiB，驱动 610.88 |
| 系统 Python | 3.13.15 |
| SDK `.venv` Python | 3.13.16 |
| `pip check` | 通过 |
| Git | 2.55.0 |
| Node | 24.21.0 |
| npm | 11.19.0 |
| uv CLI | 不在 PATH |
| Docker CLI | 不存在 |
| WSL | 未安装或不可用 |
| PostgreSQL CLI | 不存在 |
| Ollama | executable 存在，运行状态和模型未验证 |
| TypeScript `node_modules` | 不存在 |
| D 盘剩余 | 约 134.1 GB |

Python `.venv` 中四个 OpenHands 包均能导入，版本均为 1.54.0，LiteLLM 为 1.93.0。锁文件存在且 workspace、Python 版本和依赖约束结构完整。

## 10. 可复用、封装、自主开发矩阵

| 能力 | 处理方式 | 原因 |
| --- | --- | --- |
| Agent loop | 直接复用 | 上游成熟且兼容面大 |
| LLM transport | 直接复用并封装配置 | 避免重复 provider 适配 |
| Tool schema/executor | 直接复用 | 类型化实现完整 |
| Local/Remote Conversation | 适配器封装 | 隔离 1.54.0 API 变化 |
| Agent Server | 独立部署复用 | 不在业务进程内耦合私有实现 |
| TypeScript Client | 选择性复用 | 事件流有价值，高权限操作应走业务后端 |
| MCP Client | 复用并加权限策略 | 上游解决协议，本项目解决授权 |
| DockerWorkspace | 复用/封装 | 增加业务配额、审批和审计 |
| 用户/组织/RBAC | 自主开发 | 上游不负责业务身份体系 |
| PostgreSQL 数据模型 | 自主开发 | 上游核心是文件持久化 |
| RAG/pgvector/BM25 | 自主开发 | 上游不提供企业 RAG |
| Durable workflow | 自主开发/专用引擎 | 上游 workflow 是 Agent 内部编排 |
| Benchmark | 自主开发 | 需要业务任务、真实结果和统计口径 |
| 业务前端 | 自主开发 | 不复制 Agent Canvas |
| GitHub 写操作 | 自主开发且默认禁用 | 需要授权、分支和审批边界 |

## 11. 兼容性风险

1. SDK 公共 Python API、REST OpenAPI 和 TypeScript Client 是三条兼容面，必须分别固定版本。
2. 不应 import 上游私有模块或依赖私有属性。
3. RemoteConversation 的事件 schema、创建请求、settings schema 和 client tools 是重点漂移区域。
4. 上游 REST 具有五个 minor 版本的弃用规则，但新增字段仍可能影响严格校验。
5. TypeScript Client 与 Agent Server 镜像必须使用同一固定版本。
6. OpenHands 本地文件持久化不能当作本项目 PostgreSQL 的事务边界。
7. Windows native、tmux、Docker、符号链接和文件权限存在平台差异。
8. 本地小模型可能无法稳定使用完整七工具 Agent；必须有模型能力分级。

## 12. 风险登记

| 风险 | 等级 | 缓解措施 |
| --- | --- | --- |
| 无 Git commit 可追溯 | 高 | 正式开发前重新 clone/tag，记录 SHA |
| Windows 原生不完整 | 高 | WSL2 Ubuntu 作为后端主环境 |
| Docker/WSL 未安装 | 高 | 阶段 1 经用户批准后安装 |
| 业务与上游强耦合 | 高 | Anti-Corruption Layer + contract tests |
| 高权限工具越权 | 高 | ToolPolicy + RBAC + approval + sandbox |
| secrets 泄漏 | 高 | secret scan、日志脱敏、最小 scope |
| 文件持久化不适合多实例 | 高 | PostgreSQL 保存业务状态，执行事件外部索引 |
| 本地模型能力不足 | 中 | 能力路由，轻任务本地、难任务可选云模型 |
| 覆盖率无门槛 | 中 | 本项目设置增量和关键模块门槛 |
| 134 GB 磁盘被镜像/模型耗尽 | 中 | 配额、清理策略；大下载必须审批 |
| GitHub 自动化误写 | 高 | 默认 read-only，写操作逐项目授权和人工审批 |

## 13. 基线验收结论

本阶段已满足源码关系、可复用接口、环境、测试、资源和风险识别要求。尚未满足正式开发启动条件的事项是：

1. 缺少可追溯 Git clone/commit。
2. WSL2、Docker 和 PostgreSQL 未就绪。
3. 新项目尚未建立 Git 仓库，且未经用户许可不得初始化/commit/push。
4. 未执行真实 Agent Server E2E。
5. 未执行真实模型、数据库、Docker、RAG 或 GitHub 集成测试。

用户验收本报告后，方可进入环境基线和项目骨架阶段。
