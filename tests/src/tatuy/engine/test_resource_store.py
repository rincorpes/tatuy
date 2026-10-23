import pytest

from tatuy.resources import ResourceStore


class Resource:
    pass


def test_resource_store_adds_and_returns_resource_by_type():
    store = ResourceStore()
    resource = Resource()

    assert store.add(resource) is resource
    assert store.get(Resource) is resource


def test_resource_store_rejects_duplicate_resource_type():
    store = ResourceStore()
    store.add(Resource())

    with pytest.raises(ValueError, match="already registered"):
        store.add(Resource())


def test_resource_store_reports_missing_resource():
    store = ResourceStore()

    with pytest.raises(KeyError, match="is not registered"):
        store.get(Resource)
