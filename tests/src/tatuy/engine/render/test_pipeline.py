"""Render pipeline executor injection."""

from unittest.mock import Mock

from tatuy.engine.render.pipeline.pipeline import RenderPipeline
from tatuy.graphics.render.context import RenderContext


class RecordingPass:
    """Minimal pass that records the executor supplied by the pipeline."""

    name = "RecordingPass"

    def __init__(self):
        self.executor = None

    def run(self, _backend, _ctx, _packets, executor):
        self.executor = executor


def test_pipeline_passes_injected_executor_to_render_passes():
    executor = Mock()
    render_pass = RecordingPass()
    pipeline = RenderPipeline(executor=executor, passes=[render_pass])

    pipeline.render_frame_content(
        Mock(),
        RenderContext(viewport=Mock()),
        (),
    )

    assert render_pass.executor is executor
