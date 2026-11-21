# GitHub release preparation

The independent release copy contains the public backend, frontend, agent integration, deployment files, scripts, tests, dependency locks, license/notice, and documentation. Runtime data, caches, credentials, databases, model files, uploads, and `node_modules` were excluded. The Lite Compose profile is the verified default for the current 1.9 GiB Docker environment.

Evidence: source-tree inventory, forbidden-file scan, Compose configuration validation, backend Ruff (pass), and the release-copy test run (24 passed, 1 Docker Sandbox timeout caused by the local Docker lifecycle). Frontend lint/test/build passed in the source project. No Git operation or remote write was performed.

Final audit evidence: 132-file Python standard-library secrets scan passed after review of three benign field-name matches; Lite Compose config passed using external placeholder environment values; no screenshots or runtime artifacts are included. Isolated `pip-licenses` found no GPL/AGPL/proprietary/unknown license. Sandbox unit coverage passes; the sole real Docker integration test still times out in a disposable `docker run`, confirming an environment/daemon limitation without touching existing containers or volumes. Release-copy Ruff passes; 26 tests pass with that one real Docker test deselected for the non-Docker regression run.
