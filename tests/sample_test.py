"""Sample test module demonstrating pytest usage with markers and fixtures.

This module provides examples of:
- Basic pytest test functions
- Fixture usage
- Test class organization with markers
- Unit and integration test separation
"""

import pytest


def test_example():
    """Basic example test demonstrating simple assertion."""
    assert 1 + 1 == 2


@pytest.fixture
def sample_data():
    """Fixture providing sample data for tests.

    Returns:
        dict: A dictionary containing an empty packages list.
    """
    return {"packages": []}


@pytest.mark.unit
class TestSampleUnit:
    """Unit test suite demonstrating unit test organization.

    This class contains unit tests that should run in isolation.
    """

    def test_example_foo(self, sample_data):
        """Example unit test using the sample_data fixture.

        Args:
            sample_data: Fixture providing test data.
        """
        assert isinstance(sample_data, dict)


@pytest.mark.integration
class TestSampleIntegration:
    """Integration test suite demonstrating integration test organization.

    This class contains integration tests that may interact with external
    dependencies or multiple components.
    """

    def test_example_foo(self, sample_data):
        """Example integration test using the sample_data fixture.

        Args:
            sample_data: Fixture providing test data.
        """
        assert isinstance(sample_data, dict)
