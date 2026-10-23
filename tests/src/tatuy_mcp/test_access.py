from pathlib import Path

import pytest

from tatuy_mcp.access.policy import DEFAULT_ACCESS_POLICY


def test_access_policy_rejects_sensitive_paths() -> None:
    with pytest.raises(ValueError, match="excluded"):
        DEFAULT_ACCESS_POLICY.check_access(Path(".env"))

    with pytest.raises(ValueError, match="excluded"):
        DEFAULT_ACCESS_POLICY.check_access(Path(".git/config"))

    with pytest.raises(ValueError, match="excluded"):
        DEFAULT_ACCESS_POLICY.check_access(Path("keys/private.pem"))


def test_access_policy_accepts_supported_source_files() -> None:
    path = Path("src/example.py")

    DEFAULT_ACCESS_POLICY.check_access(path)

    assert DEFAULT_ACCESS_POLICY.is_searchable(path)
