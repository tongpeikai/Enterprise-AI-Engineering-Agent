import threading
from collections import Counter
from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True)
class MetricSnapshot:
    counters: dict[str, int]
    gauges: dict[str, float]
    histograms: dict[str, list[float]]

    @property
    def durations(self) -> dict[str, list[float]]:
        return self.histograms


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._counters: Counter[str] = Counter()
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}

    def increment(self, name: str, amount: int = 1) -> None:
        with self._lock:
            self._counters[name] += amount

    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value

    def observe(self, name: str, seconds: float) -> None:
        with self._lock:
            values = self._histograms.setdefault(name, [])
            if len(values) < 10_000:
                values.append(seconds)

    def timer(self, name: str):
        started = monotonic()

        class Timer:
            def __enter__(inner):
                return inner

            def __exit__(inner, *_):
                self.observe(name, monotonic() - started)

        return Timer()

    def snapshot(self) -> MetricSnapshot:
        with self._lock:
            return MetricSnapshot(
                dict(self._counters),
                dict(self._gauges),
                {key: values.copy() for key, values in self._histograms.items()},
            )
