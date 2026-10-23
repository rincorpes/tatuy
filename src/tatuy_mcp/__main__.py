from __future__ import annotations

from tatuy_mcp.server import mcp


def main() -> None:
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
    )


if __name__ == "__main__":
    main()
