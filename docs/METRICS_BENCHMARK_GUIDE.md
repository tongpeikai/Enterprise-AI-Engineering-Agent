# Metrics and Benchmark Guide

`Metrics` exposes counters, gauges and bounded histograms through immutable snapshots. The benchmark store persists tenant, kind, mode, raw result JSON and timestamp. `POST /api/v1/benchmarks/run` runs the fixed synthetic retrieval case; `GET /api/v1/benchmarks` returns persisted runs. Retrieval metrics are deterministic and separate from live model evaluation.
