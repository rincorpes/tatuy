from __future__ import annotations

import gc
from collections import deque
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from tatuy.tooling.profiler.event import ProfilerEvent
from tatuy.tooling.profiler.run import Run


@dataclass(frozen=True)
class ProfilerConfig:
    enabled: bool = False
    gc: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProfilerConfig:
        return cls(**data)


@dataclass
class RunStats:
    calls: int = 0
    total: float = 0.0
    peak: float = 0.0


class Profiler:
    _instance: Profiler | None = None
    _initialized = False

    _stack: list[Run]
    _roots: deque[Run]
    _slow_runs: list[Run]
    _stats: dict[str, RunStats]

    _active_gc_event: ProfilerEvent | None = None
    _active_gc_run: Run | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.enabled = False
        self._stack = []
        self._roots = deque(maxlen=300)
        self._slow_runs = []
        self._stats = {}

        self._slow_run_limit = 20

        self._gc_registered = False

        self._initialized = True

    def configure(self, config: ProfilerConfig):
        self.enabled = config.enabled
        if self.enabled and config.gc:
            self._register_gc_callback()
        else:
            self._unregister_gc_callback()

    @property
    def current_run(self) -> Run | None:
        if not self._stack:
            return None

        return self._stack[-1]

    def _register_gc_callback(self) -> None:
        if self._gc_registered:
            return

        gc.callbacks.append(self._on_gc)
        self._gc_registered = True

    def _unregister_gc_callback(self) -> None:
        if not self._gc_registered:
            return

        try:
            gc.callbacks.remove(self._on_gc)
        except ValueError:
            pass

        self._gc_registered = False

    def _on_gc(
        self,
        phase: str,
        info: dict[str, int],
    ) -> None:
        if not self.enabled:
            return

        if phase == "start":
            self._gc_started(info)

        elif phase == "stop":
            self._gc_finished(info)

    def _gc_started(
        self,
        info: dict[str, int],
    ) -> None:
        run = self.current_run

        if run is None:
            return

        event = ProfilerEvent(
            name="gc",
            start_time=perf_counter(),
            metadata={
                "generation": info.get("generation"),
            },
        )

        self._active_gc_event = event
        self._active_gc_run = run

    def _gc_finished(
        self,
        info: dict[str, int],
    ) -> None:
        event = self._active_gc_event
        run = self._active_gc_run

        if event is None or run is None:
            return

        event.end_time = perf_counter()

        event.metadata.update(
            {
                "collected": info.get("collected", 0),
                "uncollectable": info.get(
                    "uncollectable",
                    0,
                ),
            }
        )

        run.events.append(event)

        self._active_gc_event = None
        self._active_gc_run = None

    def start_run(
        self,
        name: str,
        run_type: str,
        *,
        parent: Run | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Run:

        run = Run(
            name=name,
            run_type=run_type,
            start_time=perf_counter(),
            metadata=metadata or {},
        )

        if parent is not None:
            run.parent_id = parent.id
            parent.children.append(run)
        else:
            self._roots.append(run)

        self._stack.append(run)

        return run

    def end_run(self, run: Run) -> None:
        run.end_time = perf_counter()

        path = "/".join(item.name for item in self._stack)

        duration = run.duration

        if duration is not None:
            stats = self._stats.setdefault(path, RunStats())

            stats.calls += 1
            stats.total += duration
            stats.peak = max(stats.peak, duration)

        popped = self._stack.pop()

        if popped is not run:
            raise RuntimeError("Profiler run stack corrupted")

        if run.parent_id is None:
            self._consider_slow_run(run)

    def _consider_slow_run(self, run: Run) -> None:
        if run.duration is None:
            return

        if run.run_type != "frame":
            return

        if not run.metadata.get("completed", False):
            return

        self._slow_runs.append(run)

        self._slow_runs.sort(
            key=lambda item: item.duration or 0.0,
            reverse=True,
        )

        del self._slow_runs[self._slow_run_limit :]

    def reset(self) -> None:
        self._stack.clear()
        self._roots.clear()
        self._slow_runs.clear()
        self._stats.clear()

        self._active_gc_event = None
        self._active_gc_run = None

    @contextmanager
    def trace(
        self,
        name: str,
        run_type: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> Iterator[Run | None]:

        if not self.enabled:
            yield None
            return

        run = self.start_run(
            name,
            run_type,
            parent=None,
            metadata=metadata,
        )

        try:
            yield run
        finally:
            self.end_run(run)

    @contextmanager
    def span(
        self,
        name: str,
        run_type: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> Iterator[Run | None]:

        if not self.enabled:
            yield None
            return

        parent = self.current_run

        if parent is None:
            raise RuntimeError(
                "Profiler span requires an active trace or span"
            )

        run = self.start_run(
            name,
            run_type,
            parent=parent,
            metadata=metadata,
        )

        try:
            yield run
        finally:
            self.end_run(run)

    def traces_over(
        self,
        name: str,
        duration_ms: float,
    ) -> list[Run]:
        threshold = duration_ms / 1000.0

        return sorted(
            (
                run
                for run in self._roots
                if (
                    run.name == name
                    and run.duration is not None
                    and run.duration >= threshold
                )
            ),
            key=lambda run: run.duration or 0.0,
            reverse=True,
        )

    def get_frame(self, frame_index: int) -> Run | None:
        for run in self._roots:
            if (
                run.run_type == "frame"
                and run.metadata.get("frame") == frame_index
            ):
                return run

        return None

    def format_trace(self, root: Run) -> str:
        lines: list[str] = []

        root_duration = root.duration

        if root_duration is None:
            return f"{root.name}: incomplete"

        header = (
            f"{'Trace':<62}"
            f"{'Total ms':>12}"
            f"{'Self ms':>12}"
            f"{'Work ms':>12}"
            f"{'% frame':>10}"
        )

        lines.append(header)
        lines.append("-" * len(header))

        def visit(
            run: Run,
            depth: int = 0,
        ) -> None:
            duration = run.duration

            if duration is None:
                return

            self_duration = run.self_duration or 0.0
            work_duration = run.work_duration or 0.0
            percent = duration / root_duration * 100.0

            name = f"{'  ' * depth}{run.name}"

            lines.append(
                f"{name:<62}"
                f"{duration * 1000:>12.3f}"
                f"{self_duration * 1000:>12.3f}"
                f"{work_duration * 1000:>12.3f}"
                f"{percent:>9.2f}%"
            )

            # Runtime events that happened while this run was active.
            for event in run.events:
                event_duration = event.duration

                if event_duration is None:
                    continue

                generation = event.metadata.get("generation", "?")
                collected = event.metadata.get("collected", 0)
                uncollectable = event.metadata.get("uncollectable", 0)

                event_name = (
                    f"{'  ' * (depth + 1)}"
                    f"! {event.name} "
                    f"gen={generation} "
                    f"collected={collected} "
                    f"uncollectable={uncollectable}"
                )

                event_percent = event_duration / root_duration * 100.0

                lines.append(
                    f"{event_name:<62}"
                    f"{event_duration * 1000:>12.3f}"
                    f"{'':>12}"
                    f"{'':>12}"
                    f"{event_percent:>9.2f}%"
                )

            for child in run.children:
                visit(child, depth + 1)

            if run.metrics:
                metrics = " ".join(
                    f"{name}={value}" for name, value in run.metrics.items()
                )

                metric_name = f"{'  ' * (depth + 1)}" f"· {metrics}"

                lines.append(metric_name)

            if run.metadata:
                metadata = " ".join(
                    f"{name}={value}"
                    for name, value in run.metadata.items()
                    if name not in {"frame", "completed"}
                )

                if metadata:
                    metadata_name = f"{'  ' * (depth + 1)}" f"@ {metadata}"

                    lines.append(metadata_name)

        visit(root)

        return "\n".join(lines)

    def format_slowest(
        self,
        name: str,
        *,
        limit: int = 10,
        completed_only: bool = True,
    ) -> str:
        runs = self.slowest(name, limit=limit, completed_only=completed_only)

        if not runs:
            return f"No completed {name!r} traces."

        lines: list[str] = []

        for index, run in enumerate(runs, start=1):
            duration_ms = (run.duration or 0.0) * 1000.0

            if lines:
                lines.append("")

            if run.run_type == "frame":
                frame_index = run.metadata.get("frame", "?")
                title = (
                    f"#{index} — Frame {frame_index} — "
                    f"{duration_ms:.3f} ms"
                )
            else:
                title = f"#{index} — {run.name} — " f"{duration_ms:.3f} ms"

            lines.append(title)
            lines.append("=" * len(title))
            lines.append(self.format_trace(run))

        return "\n".join(lines)

    def slowest(
        self,
        name: str,
        *,
        limit: int = 10,
        completed_only: bool = False,
    ) -> list[Run]:
        runs = [
            run
            for run in self._slow_runs
            if (
                run.name == name
                and run.duration is not None
                and (
                    not completed_only or run.metadata.get("completed", False)
                )
            )
        ]

        return runs[:limit]

    def report(self) -> str:
        if not self._stats:
            return "Profiler: no completed runs."

        trace_width = max(
            42,
            max(len(name) for name in self._stats) + 2,
        )

        header = (
            f"{'Trace':<{trace_width}} "
            f"{'Calls':>7} "
            f"{'Avg ms':>10} "
            f"{'Max ms':>10} "
            f"{'Total ms':>12}"
        )

        lines = [header, "-" * len(header)]

        for name, stats in self._stats.items():
            lines.append(
                f"{name:<{trace_width}} "
                f"{stats.calls:>7} "
                f"{stats.total / stats.calls * 1000:>10.3f} "
                f"{stats.peak * 1000:>10.3f} "
                f"{stats.total * 1000:>12.3f}"
            )

        return "\n".join(lines)

    def annotate(
        self,
        **metadata: Any,
    ) -> None:
        if not self.enabled:
            return

        run = self.current_run

        if run is None:
            return

        run.metadata.update(metadata)

    def metric(
        self,
        name: str,
        value: float | int,
    ) -> None:
        if not self.enabled:
            return

        run = self.current_run

        if run is None:
            return

        run.metrics[name] = value

    def increment(
        self,
        name: str,
        value: float | int = 1,
    ) -> None:
        if not self.enabled:
            return

        run = self.current_run

        if run is None:
            return

        run.metrics[name] = run.metrics.get(name, 0) + value
