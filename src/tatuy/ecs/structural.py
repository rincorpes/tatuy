from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Generic

from tatuy.ecs.entity import EntityId
from tatuy.scenes.context import TContext


class StructuralCommand(ABC, Generic[TContext]):
    @abstractmethod
    def execute(self, ctx: TContext) -> None:
        raise NotImplementedError


@dataclass(frozen=True)
class AddComponent(StructuralCommand[TContext]):
    entity: EntityId
    component: object

    def execute(self, ctx: TContext) -> None:
        ctx.world.add_component(self.entity, self.component)


@dataclass(frozen=True)
class RemoveComponent(StructuralCommand[TContext]):
    entity: EntityId
    component_type: type

    def execute(self, ctx: TContext) -> None:
        ctx.world.remove_component(
            self.entity,
            self.component_type,
        )


class StructuralCommandBuffer(Generic[TContext]):
    def __init__(self) -> None:
        self._pending: deque[StructuralCommand[TContext]] = deque()

    def enqueue(
        self,
        command: StructuralCommand[TContext],
    ) -> None:
        self._pending.append(command)

    def commit(self, ctx: TContext) -> None:
        # Process only commands pending at this barrier.
        for _ in range(len(self._pending)):
            command = self._pending.popleft()
            command.execute(ctx)
