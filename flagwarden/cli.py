from __future__ import annotations

import argparse
import os
from pathlib import Path

from .challenges import validate_pack
from .config import get_settings
from .security import answer_digest


def main() -> None:
    parser = argparse.ArgumentParser(prog="flagwarden")
    sub = parser.add_subparsers(dest="command", required=True)

    pack = sub.add_parser("pack")
    pack_sub = pack.add_subparsers(dest="pack_command", required=True)
    validate = pack_sub.add_parser("validate")
    validate.add_argument("path")

    answer = sub.add_parser("answer")
    answer_sub = answer.add_subparsers(dest="answer_command", required=True)
    digest = answer_sub.add_parser("digest")
    digest.add_argument("answer")

    args = parser.parse_args()
    if args.command == "pack" and args.pack_command == "validate":
        metadata, challenges = validate_pack(Path(args.path))
        print(f"OK: {metadata.name} {metadata.version} — {len(challenges)} challenges")
        for c in challenges:
            print(f"  - {c.id}: {c.title} [{c.difficulty}]")
    elif args.command == "answer" and args.answer_command == "digest":
        print(answer_digest(args.answer, get_settings().answer_pepper))


if __name__ == "__main__":
    main()
