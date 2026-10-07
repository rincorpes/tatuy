from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Iterable,
    Protocol,
    TypeVar,
)

from tatuy.ecs.system import BaseSystem, GameSystem, SystemPhase
from tatuy.scenes.context import SceneTickContext, TContext

TContext_contra = TypeVar(
    "TContext_contra",
    bound=SceneTickContext[Any, Any],
    contravariant=True,
)

PHASE_METHODS = {
    SystemPhase.CONTROL: "on_control",
    SystemPhase.PRE_SIMULATION: "on_pre_simulation",
    SystemPhase.SIMULATION: "on_simulation",
    SystemPhase.POST_SIMULATION: "on_post_simulation",
    SystemPhase.PRESENTATION: "on_presentation",
}

UPDATE_PHASES = tuple(
    phase for phase in SystemPhase if phase != SystemPhase.PRESENTATION
)

COMMIT_PHASES = {
    SystemPhase.PRE_SIM_COMMIT,
    SystemPhase.POST_SIM_COMMIT,
}


@dataclass(frozen=True)
class SystemRegistration(Generic[TContext]):
    system: BaseSystem[TContext] | GameSystem[TContext]

    # Built-ins can override their existing scheduling metadata.
    phase: SystemPhase | None = None
    order: int | None = None

    # Automatic activation, separate from system.enabled().
    active: Callable[[TContext], bool] | None = None

    PHASE_METHODS: ClassVar[dict[SystemPhase, str]] = {
        SystemPhase.CONTROL: "on_control",
        SystemPhase.PRE_SIMULATION: "on_pre_simulation",
        SystemPhase.SIMULATION: "on_simulation",
        SystemPhase.POST_SIMULATION: "on_post_simulation",
        SystemPhase.PRESENTATION: "on_presentation",
    }

    def build_steps(
        self,
        sequence: int,
    ) -> Iterable[tuple[SystemPhase, ScheduledStep[TContext]]]:
        if isinstance(self.system, BaseSystem):
            phase = self.system.phase if self.phase is None else self.phase

            yield phase, self._build_step(
                callback=self.system.step,
                order=self._default_order(),
                sequence=sequence,
            )
            return

        if not isinstance(self.system, GameSystem):
            raise TypeError(
                f"Unsupported system: {type(self.system).__name__}"
            )

        if self.phase is not None:
            raise ValueError("Game systems derive phases from their methods")

        for phase, method_name in self.PHASE_METHODS.items():
            implementation = getattr(type(self.system), method_name)
            default = getattr(GameSystem, method_name)

            if implementation is default:
                continue

            yield phase, self._build_step(
                callback=getattr(self.system, method_name),
                order=self.system.phase_orders.get(
                    phase, self._default_order()
                ),
                sequence=sequence,
            )

    def _default_order(self) -> int:
        return self.system.order if self.order is None else self.order

    def _build_step(
        self,
        *,
        callback: Callable[[TContext], None],
        order: int,
        sequence: int,
    ) -> ScheduledStep[TContext]:
        return ScheduledStep(
            owner=self.system,
            callback=callback,
            order=order,
            sequence=sequence,
            active=self.active,
        )


@dataclass(frozen=True)
class ScheduledStep(Generic[TContext]):
    owner: BaseSystem[TContext] | GameSystem[TContext]
    callback: Callable[[TContext], None]
    order: int
    sequence: int
    active: Callable[[TContext], bool] | None = None

    def execute(self, ctx: TContext) -> None:
        if self.active is not None and not self.active(ctx):
            return

        if self.owner.enabled(ctx):
            self.callback(ctx)

    def sort_key(self) -> tuple[int, str, int]:
        return self.order, self.owner.name, self.sequence


class StructuralCommitter(Protocol[TContext_contra]):
    def commit(self, ctx: TContext_contra) -> None: ...


class SystemPipeline(Generic[TContext]):
    UPDATE_PHASES = (
        SystemPhase.CONTROL,
        SystemPhase.PRE_SIMULATION,
        SystemPhase.PRE_SIM_COMMIT,
        SystemPhase.SIMULATION,
        SystemPhase.POST_SIMULATION,
        SystemPhase.POST_SIM_COMMIT,
    )

    COMMIT_PHASES = (
        SystemPhase.PRE_SIM_COMMIT,
        SystemPhase.POST_SIM_COMMIT,
    )

    def __init__(
        self,
        committer: StructuralCommitter[TContext],
        registrations: Iterable[SystemRegistration[TContext]] = (),
    ) -> None:
        self._committer = committer
        self._next_sequence = 0
        self._steps: dict[SystemPhase, list[ScheduledStep[TContext]]] = {
            phase: [] for phase in SystemPhase
        }

        self.extend(registrations)

    def add(
        self,
        registration: SystemRegistration[TContext],
    ) -> None:
        self._register(registration)
        self._sort()

    def extend(
        self,
        registrations: Iterable[SystemRegistration[TContext]],
    ) -> None:
        for registration in registrations:
            self._register(registration)

        self._sort()

    def update(self, ctx: TContext) -> None:
        for phase in self.UPDATE_PHASES:
            self.run_phase(phase, ctx)

    def present(self, ctx: TContext) -> None:
        self.run_phase(SystemPhase.PRESENTATION, ctx)

    def run_phase(
        self,
        phase: SystemPhase,
        ctx: TContext,
    ) -> None:
        for step in self._steps[phase]:
            step.execute(ctx)

        if phase in self.COMMIT_PHASES:
            self._committer.commit(ctx)

    def _register(
        self,
        registration: SystemRegistration[TContext],
    ) -> None:
        sequence = self._next_sequence

        # Build before modifying the schedule so invalid
        # registrations cannot leave partially added steps.
        steps = tuple(registration.build_steps(sequence))

        for phase, step in steps:
            self._steps[phase].append(step)

        self._next_sequence += 1

    def _sort(self) -> None:
        for steps in self._steps.values():
            steps.sort(key=ScheduledStep.sort_key)
