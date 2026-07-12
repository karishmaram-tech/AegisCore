"""``python -m aegiscore.skillogy.builder`` entrypoint."""

from __future__ import annotations

import sys

from aegiscore.skillogy.builder.cli import main

if __name__ == "__main__":
    sys.exit(int(main()))
