"""Window setup retains the SDL wrapper and follows display dimensions."""

from types import SimpleNamespace
from unittest.mock import Mock

from tatuy.backend.pygame.components import window as module
from tatuy.backend.pygame.config import PygameWindowConfig


def test_window_open_resize_and_title(monkeypatch):
    screen = Mock()
    screen.get_size.return_value = (20, 10)
    platform = Mock(RESIZABLE=16)
    platform.display.set_mode.return_value = screen
    wrapper = SimpleNamespace(position=(3, 4))
    wrapper_type = Mock()
    wrapper_type.from_display_module.return_value = wrapper
    monkeypatch.setattr(module, "pygame", platform)
    monkeypatch.setattr(module, "Window", wrapper_type)
    window = module.PygameWindow(
        PygameWindowConfig(
            width=20,
            height=10,
            title="test",
            resizable=True,
        )
    )
    platform.display.set_mode.assert_not_called()
    window.open()
    platform.display.set_mode.assert_called_once_with((20, 10), 16)
    assert window.position.to_tuple() == (3.0, 4.0)
    assert window._sdl_window is wrapper
    assert window.size.to_tuple() == (20, 10)
    window.set_title("new")
    platform.display.set_caption.assert_called_with("new")
    window.resize(30, 15)
    platform.display.set_mode.assert_called_with((30, 15), 16)
    screen.get_size.return_value = (30, 15)
    assert window.size.to_tuple() == (30, 15)
