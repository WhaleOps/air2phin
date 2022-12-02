from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from airtolphin.constants import REGEXP
from airtolphin.runner import run


def build_argparse() -> argparse.ArgumentParser:
    """Build argparse.ArgumentParser with specific configuration."""
    parser = argparse.ArgumentParser(
        prog="airtolphin",
        description="A tool covert Airflow DAGs to DolphinScheduler Python API definition.",
    )

    parser.add_argument(
        "sources",
        default=[Path("")],
        nargs="*",
        help="Enter the directories and file paths you want to convert.",
        action="store",
        type=Path,
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_argparse()
    argv = argv if argv is not None else sys.argv[1:]
    args = parser.parse_args(argv)

    counter = 0
    for path in args.sources:
        if not path.exists():
            raise ValueError("Path %s does not exist.", path)

        if path.is_file():
            run(path)
            counter += 1
        else:
            for file in path.glob(REGEXP.PATH_PYTHON):
                run(file)
                counter += 1
    print(f"Covert {counter} files done.")


if __name__ == "__main__":
    raise SystemExit(main())
