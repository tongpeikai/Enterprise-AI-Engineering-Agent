# Benchmark guide

Run deterministic retrieval benchmarks through `POST /api/v1/benchmarks/run`; inspect raw JSON and the generated report endpoint. Mock and live Agent Server runs must be labelled separately. Metrics such as Recall@K and MRR describe the supplied evaluation set only, not production performance.
