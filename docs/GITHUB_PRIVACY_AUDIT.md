# GitHub privacy audit

- Scope: all 130 files in this release copy after runtime-artifact exclusion.
- `.env` and environment-specific files: excluded; only `.env.example` is present.
- Databases, logs, uploads, model files, Docker data, caches, `node_modules`, `dist`, bytecode and test caches: excluded.
- Credential scan: no credential-like matches in public source; values are not reproduced in this report.
- Personal paths and runtime reports: excluded from the release copy.
- Git history/remotes: no Git history or remote was copied or created in the release directory.
- Frontend bundle: build output is excluded; no Vite secret variables are published.
- License/notice: retained and reviewed.

## Final checks

- Secrets scanner: PASS, 132 files scanned by a Python standard-library scanner. Three benign context matches (`password` field names and environment-variable reads) were reviewed; no credential values, tokens, private keys, or personal paths were present. `gitleaks`/`trufflehog` binaries were unavailable.
- Git tracking/history: PASS; no `.git` directory, commits, or remotes are present in the release copy.
- Dependency license tooling: PASS; isolated `pip-licenses` run over the locked runtime export found only MIT/BSD/Apache-2.0/PSF-2.0/MPL-2.0 licenses.
- Screenshots/private media: PASS; no image files are present.
- Docker/PowerShell credential review: PASS; values are environment-driven and placeholders only.

Status: PASS for privacy controls and dependency license compatibility. Dedicated secrets binaries remain unavailable; human review is still required before any public commit.
