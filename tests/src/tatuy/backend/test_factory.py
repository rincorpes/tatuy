"""Factory discovery without changing the global registry."""

from unittest.mock import Mock

import pytest

from tatuy.backend import factory


@pytest.fixture
def registry(monkeypatch):
    fake = Mock()
    monkeypatch.setattr(factory, "BackendRegistry", fake)
    return fake


def test_registered_builder_receives_original_config(registry):
    registry.contains.return_value = True
    builder_type = registry.get.return_value
    config = {"window": {"width": 32}}
    result = factory.BackendFactory.create(" PYGAME ", config)
    registry.contains.assert_called_once_with("pygame")
    registry.get.assert_called_once_with("pygame")
    builder_type.return_value.build.assert_called_once_with(config)
    assert result is builder_type.return_value.build.return_value


@pytest.mark.parametrize("name", ["", "_private", "../pygame", "a.b"])
def test_unregistered_invalid_names_do_not_import(name, registry, monkeypatch):
    registry.contains.return_value = False
    importer = Mock()
    monkeypatch.setattr(factory, "import_module", importer)
    with pytest.raises(ValueError, match="Invalid backend name"):
        factory.BackendFactory.create(name, {})
    importer.assert_not_called()


def test_lazy_discovery_imports_builder(registry, monkeypatch):
    registry.contains.return_value = False
    importer = Mock()
    monkeypatch.setattr(factory, "import_module", importer)
    factory.BackendFactory.create("future", {})
    importer.assert_called_once_with("tatuy.backend.future.builder")


@pytest.mark.parametrize(
    "missing",
    [
        "tatuy.backend.future",
        "tatuy.backend.future.builder",
    ],
)
def test_unknown_backend_has_context(missing, registry, monkeypatch):
    registry.contains.return_value = False
    error = ModuleNotFoundError("missing", name=missing)
    monkeypatch.setattr(factory, "import_module", Mock(side_effect=error))
    with pytest.raises(ValueError, match="Unknown backend") as caught:
        factory.BackendFactory.create("future", {})
    assert caught.value.__cause__ is error


def test_missing_dependency_is_not_misreported(registry, monkeypatch):
    registry.contains.return_value = False
    error = ModuleNotFoundError("missing", name="native_dependency")
    monkeypatch.setattr(factory, "import_module", Mock(side_effect=error))
    with pytest.raises(ModuleNotFoundError) as caught:
        factory.BackendFactory.create("future", {})
    assert caught.value is error


def test_import_without_registration_is_reported(registry, monkeypatch):
    registry.contains.return_value = False
    registry.get.side_effect = KeyError("future")
    monkeypatch.setattr(factory, "import_module", Mock())
    with pytest.raises(ValueError, match="did not register"):
        factory.BackendFactory.create("future", {})
