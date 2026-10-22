"""Concrete builder conversion does not initialize platform devices."""

from unittest.mock import Mock

from tatuy.backend.pygame import builder
from tatuy.backend.pygame.config import PygameBackendConfig


def test_builder_uses_concrete_config_without_init(monkeypatch):
    backend_type = Mock()
    monkeypatch.setattr(builder, "PygameBackend", backend_type)
    result = builder.PygameBackendBuilder().build({"window": {"width": 32}})
    config = backend_type.call_args.args[0]
    assert isinstance(config, PygameBackendConfig)
    assert config.window.width == 32
    assert result is backend_type.return_value
    result.init.assert_not_called()
