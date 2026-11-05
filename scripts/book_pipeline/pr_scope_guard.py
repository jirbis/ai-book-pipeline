#!/usr/bin/env python3
"""Validate scope of book-labeled PRs using authoritative API data, before merge.

Run exclusively from trusted default branch with read-only token. Never
checkout PR code. Return 2 to block a malformed/out-of-scope book PR.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from router import preflight


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", required=True, type=Path)
    parser.add_argument("--files", required=True, type=Path)
    parser.add_argument("--books-prefix", default="books")
    args = parser.parse_args(argv)
    try:
        pr = json.loads(args.pr.read_text(encoding="utf-8"))
        paths = json.loads(args.files.read_text(encoding="utf-8"))
        outcome = preflight(pr, paths, books_prefix=args.books_prefix)
        print(json.dumps(outcome, indent=2, sort_keys=True))
        return 0 if outcome["status"] in {"ok", "skip"} else 2
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("Pre-merge book scope guard failed closed: " + type(exc).__name__,
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
