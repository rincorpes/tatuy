from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from tatuy.tooling.profiler.run import Run


@dataclass(frozen=True)
class ProfilerConfig:
    enabled: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProfilerConfig:
        return cls(**data)


class Profiler:
    _instance: Profiler | None = None
    _initialized = False

    _stack: list[Run]
    _roots: list[Run]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.enabled = False
        self._stack = []
        self._roots = []

        self._initialized = True

    def configure(self, config: ProfilerConfig):
        self.enabled = config.enabled

    @property
    def current_run(self) -> Run | None:
        if not self._stack:
            return None

        return self._stack[-1]

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

        popped = self._stack.pop()

        if popped is not run:
            raise RuntimeError("Profiler run stack corrupted")

    def reset(self) -> None:
        self._stack.clear()
        self._roots.clear()

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
            f"{'Trace':<42}"
            f"{'Total ms':>12}"
            f"{'Self ms':>12}"
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
            percent = duration / root_duration * 100.0

            name = f"{'  ' * depth}{run.name}"

            lines.append(
                f"{name:<42}"
                f"{duration * 1000:>12.3f}"
                f"{self_duration * 1000:>12.3f}"
                f"{percent:>9.2f}%"
            )

            for child in run.children:
                visit(child, depth + 1)

        visit(root)

        return "\n".join(lines)

    def format_slowest(
        self,
        name: str,
        *,
        limit: int = 10,
        completed_only=True,
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
            for run in self._roots
            if (
                run.name == name
                and run.duration is not None
                and (
                    not completed_only or run.metadata.get("completed", False)
                )
            )
        ]

        return sorted(
            runs,
            key=lambda run: run.duration or 0.0,
            reverse=True,
        )[:limit]

    def report(self) -> str:
        stats: dict[str, tuple[int, float, float]] = {}

        def collect(run: Run, parent: str = "") -> None:
            name = f"{parent}/{run.name}" if parent else run.name
            duration = run.duration

            if duration is not None:
                count, total, peak = stats.get(name, (0, 0.0, 0.0))
                stats[name] = (
                    count + 1,
                    total + duration,
                    max(peak, duration),
                )

            for child in run.children:
                collect(child, name)

        for root in self._roots:
            collect(root)

        if not stats:
            return "Profiler: no completed runs."

        trace_width = max(42, max(len(name) for name in stats) + 2)

        header = (
            f"{'Trace':<{trace_width}} {'Calls':>7} {'Avg ms':>10} "
            f"{'Max ms':>10} {'Total ms':>12}"
        )

        lines = [header, "-" * len(header)]

        for name, (count, total, peak) in stats.items():
            lines.append(
                f"{name:<{trace_width}} {count:>7} "
                f"{total / count * 1000:>10.3f} "
                f"{peak * 1000:>10.3f} {total * 1000:>12.3f}"
            )

        return "\n".join(lines)
