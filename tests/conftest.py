"""Module to trigger global pytest configurations"""

import pytest


def pytest_sessionstart(session):
    """
    This function is called when pytest session starts.
    """


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    This function is called when pytest runtest makes a report.
    """


def pytest_sessionfinish(session, exitstatus):
    """
    This function is called when pytest session finishes.
    """
