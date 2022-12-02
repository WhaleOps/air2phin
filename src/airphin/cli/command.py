import argparse
import sys
from pathlib import Path
from typing import Sequence

from airphin.constants import REGEXP
from airphin.core.rules.loader import all_rules, path_rule
from airphin.runner import run


def build_argparse() -> argparse.ArgumentParser:
    """Build argparse.ArgumentParser with specific configuration."""
    parser = argparse.ArgumentParser(
        prog="airphin",
        description="A tool convert Airflow DAGs to DolphinScheduler Python API definition.",
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        help="Choose one of the subcommand you want to run.",
    )

    # Convert
    parser_convert = subparsers.add_parser("convert", help="Convert DAGs definition.")
    parser_convert.add_argument(
        "sources",
        default=[Path(".")],
        nargs="*",
        help="Enter the directories and file paths you want to convert.",
        action="store",
        type=Path,
    )

    # Rule
    parser_rule = subparsers.add_parser("rule", help="Rule of converting.")
    parser_rule.add_argument(
        "--show",
        "-s",
        action="store_true",
        help="Show all rules for converting.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_argparse()
    argv = argv if argv is not None else sys.argv[1:]
    # args = parser.parse_args(["rule", "--show"])
    args = parser.parse_args(argv)

    counter = 0

    if args.subcommand == "convert":
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
        print(f"Convert {counter} files done.")

    if args.subcommand == "rule":
        if args.show:
            rules = all_rules()
            print(f"Total {len(rules)} rules:\n")
            for rule in rules:
                print(rule.relative_to(path_rule))


if __name__ == "__main__":
    raise SystemExit(main())
