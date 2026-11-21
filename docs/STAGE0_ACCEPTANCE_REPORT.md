# Stage 0 Acceptance Report

Date: 2026-11-20 (Asia/Shanghai)

## Results

| Area | Status | Verified result |
|---|---|---|
| Independent project repository | PASS | Local Git repository initialized; no remote and no commit |
| OpenHands pinning | PASS | Agent Server 1.54.0 image pinned by digest; server reports SDK/tools/workspace 1.54.0 and build SHA `1d471742ea7be017d013eaaa3080f5d28d5490cb` |
| PostgreSQL | PASS | pgvector/pg17 container healthy on localhost:5433 |
| pgvector extension | PASS | Extension 0.8.7 enabled |
| Database CRUD | PASS | Insert/select/delete vector probe succeeded |
| Agent Server health | PASS | `/health`, `/openapi.json`, `/server_info` returned successfully |
| REST conversation creation | PASS | Authenticated conversation created with non-paid placeholder model and no initial LLM call |
| WebSocket | PASS | Authenticated `/sockets/events/{id}` connection received initial full-state event |
| Independent deterministic Mock Agent | PASS | Local harness executed a scripted tool call and recorded user/tool/result/final event order; `1 passed`, Ruff clean |
| Agent Server Mock LLM execution | NOT TESTED | Published server image has no injected mock transport; no paid API was used |
| Tool execution | NOT TESTED | No model action was issued; server advertises terminal/file/browser tools |
| Pause/resume | NOT TESTED | Requires an active model-driven run |
| WSL2 | BLOCKED | WSL app package unavailable; Docker runs via Hyper-V fallback |
| Windows GPU path | NOT TESTED | No model or CUDA workload downloaded |

## Corrective action completed

The server state volume initially had a UID mismatch. It was corrected to the image runtime UID (10001) without changing upstream source, after which authenticated conversation creation succeeded.

## Stage 0 conclusion

Core infrastructure, database, REST and WebSocket connectivity are operational. The independent deterministic Mock Agent baseline is now verified. Full server-side model/tool/pause verification remains unavailable because the pinned image has no injected mock transport and paid APIs are prohibited. Stage 1 should wrap this harness behind the Agent Gateway contract before any real provider integration.
