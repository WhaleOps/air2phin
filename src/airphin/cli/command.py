import argparse
import difflib
import sys
from pathlib import Path
from typing import Sequence

from airphin import __description__, __project_name__, __version__
from airphin.constants import REGEXP
from airphin.core.rules.loader import all_rules, path_rule
from airphin.runner import with_file, with_str


def build_argparse() -> argparse.ArgumentParser:
    """Build argparse.ArgumentParser with specific configuration."""
    parser = argparse.ArgumentParser(
        prog="airphin",
        description=__description__,
    )

    # Version
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{__project_name__} version {__version__}",
        help="Show version of %(prog)s.",
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        help="Choose one of the subcommand you want to run.",
    )

    # Test
    parser_convert = subparsers.add_parser(
        "test", help="Test or play convert with standard input."
    )
    parser_convert.add_argument(
        "-d",
        "--diff",
        action="store_true",
        help=f"Prints a diff of all changes {__project_name__} would make to a file.",
    )
    parser_convert.add_argument(
        "stdin",
        help="Enter the standard input you want to convert.",
        action="store",
        type=str,
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
        "-s",
        "--show",
        action="store_true",
        help="Show all rules for converting.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Run airphin in command line."""
    parser = build_argparse()
    argv = argv if argv is not None else sys.argv[1:]
    # args = parser.parse_args(["rule", "--show"])
    args = parser.parse_args(argv)

    if args.subcommand == "test":
        stdin = args.stdin
        result = with_str(stdin)
        print(f"\nConverted result is: \n\n{result}")

        if args.diff:
            diff = difflib.unified_diff(
                stdin.splitlines(keepends=True),
                result.splitlines(keepends=True),
                fromfile="source",
                tofile="dest",
            )
            print(f"\nThe diff is: \n{''.join(diff)}")

    if args.subcommand == "convert":
        counter = 0
        for path in args.sources:
            if not path.exists():
                raise ValueError("Path %s does not exist.", path)

            if path.is_file():
                with_file(path)
                counter += 1
            else:
                for file in path.glob(REGEXP.PATH_PYTHON):
                    with_file(file)
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
