from __future__ import annotations

import sys
from pathlib import Path

from tatuy_cli.commands.create.input import CreateTargetInput
from tatuy_cli.scaffolding import CreateTargetRequest, TargetScaffolder

THIS_FILE = Path(__file__).resolve()
ENGINE_ROOT = THIS_FILE.parents[4]


class CreateTargetOperation:
    def execute(
        self,
        input_data: CreateTargetInput,
    ) -> int:
        destination = Path(input_data.path) if input_data.path else None

        request = CreateTargetRequest(
            kind=input_data.kind,
            name=input_data.name,
            description=input_data.description,
            tags=input_data.tags,
            destination=destination,
            tatuy_source=input_data.tatuy_source,
            tatuy_version=input_data.tatuy_version,
        )

        try:
            result = TargetScaffolder(
                engine_root=ENGINE_ROOT,
            ).create(request)
        except (OSError, ValueError) as error:
            print(error, file=sys.stderr)
            return 1

        print(f"Created {result.kind} " f"'{result.name}' at {result.path}")

        print(f"Run with: {result.run_command}")

        return 0
