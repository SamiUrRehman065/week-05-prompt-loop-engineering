import argparse
import sys
from pathlib import Path

from triage import triage_claim


def read_claim(args: argparse.Namespace) -> str:
    if args.claim:
        return " ".join(args.claim)

    if args.file:
        return Path(args.file).read_text(encoding="utf-8")

    print("Type the claim and press Enter:")
    return input("> ")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preliminary insurance-claim triage with a local Ollama model."
    )
    parser.add_argument(
        "claim",
        nargs="*",
        help="claim text (leave empty to type it in)",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="read the claim text from a file",
    )
    args = parser.parse_args()

    outcome = triage_claim(read_claim(args))
    print(outcome.model_dump_json(indent=2))

    return 0 if outcome.status == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
