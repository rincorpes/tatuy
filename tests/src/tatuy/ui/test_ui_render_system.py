from unittest.mock import Mock

from tatuy.ui.systems import UiRenderSystem


def test_ui_render_system_delegates_to_ui_renderer():
    system = UiRenderSystem()
    system._renderer = Mock()

    ctx = Mock()
    ctx.world = Mock()
    ctx.render_queue = Mock()

    system.step(ctx)

    system._renderer.submit.assert_called_once_with(
        ctx.world,
        ctx.render_queue,
    )
