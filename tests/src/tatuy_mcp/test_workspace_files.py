from tatuy_mcp.workspace.files import WorkspaceFiles


def test_normalize_newlines_matches_crlf_target_style() -> None:
    text = "first\nsecond\n"

    assert WorkspaceFiles._normalize_newlines(text, "\r\n") == (
        "first\r\nsecond\r\n"
    )


def test_normalize_newlines_matches_lf_target_style() -> None:
    text = "first\r\nsecond\r\n"

    assert WorkspaceFiles._normalize_newlines(text, "\n") == "first\nsecond\n"
