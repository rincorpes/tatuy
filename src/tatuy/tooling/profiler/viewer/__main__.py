from __future__ import annotations

import sys
import webbrowser

from tatuy.tooling.profiler.viewer.server import serve


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m " "tatuy.tooling.profiler.viewer <profile.json>"
        )

    profile_path = sys.argv[1]

    webbrowser.open("http://127.0.0.1:8765")

    serve(profile_path)


if __name__ == "__main__":
    main()
