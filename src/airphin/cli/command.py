import argparse
import difflib
import sys
from pathlib import Path
from typing import Sequence

from airphin import __project_name__, __version__
from airphin.constants import REGEXP
from airphin.core.rules.config import Config
from airphin.core.rules.loader import build_in_rules, path_rule
from airphin.runner import Runner


def build_argparse() -> argparse.ArgumentParser:
    """Build argparse.ArgumentParser with specific configuration."""
    parser = argparse.ArgumentParser(
        prog="airphin",
        description="Airphin is a tool for converting Airflow DAGs to DolphinScheduler Python API.",
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
        help=f"Subcommand you want to {__project_name__} to run.",
    )

    # Test
    parser_convert = subparsers.add_parser(
        "test", help=f"Play with {__project_name__} convert with standard input."
    )
    parser_convert.add_argument(
        "-r",
        "--rules",
        help=f"The custom rule file path you want to add to {__project_name__}.",
        action="store",
        type=Path,
    )
    parser_convert.add_argument(
        "-d",
        "--diff",
        action="store_true",
        help=f"Prints diff of all the changes {__project_name__} would make.",
    )
    parser_convert.add_argument(
        "stdin",
        help="The standard input you want to convert.",
        action="store",
        type=str,
    )

    # Convert
    parser_convert = subparsers.add_parser("convert", help="Convert DAGs definition.")
    parser_convert.add_argument(
        "-r",
        "--rules",
        help=f"The custom rule file path you want to add to {__project_name__}.",
        action="store",
        type=Path,
    )
    parser_convert.add_argument(
        "sources",
        default=[Path(".")],
        nargs="*",
        help="The directories or files paths you want to convert.",
        action="store",
        type=Path,
    )

    # Rule
    parser_rule = subparsers.add_parser("rule", help="Rule of converting.")
    parser_rule.add_argument(
        "-s",
        "--show",
        action="store_true",
        help=f"Show all rules for {__project_name__} convert.",
    )

    return parser


def main(argv: Sequence[str] = None) -> None:
    """Run airphin in command line."""
    parser = build_argparse()
    argv = argv if argv is not None else sys.argv[1:]
    # args = parser.parse_args(["rule", "--show"])
    args = parser.parse_args(argv)

    customs_rules = [args.rules] if args.rules else []

    if args.subcommand == "test":
        stdin = args.stdin
        config = Config(customs=customs_rules)
        runner = Runner(config)

        result = runner.with_str(stdin)
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

            config = Config(customs=customs_rules)
            runner = Runner(config)
            if path.is_file():
                runner.with_file(path)
                counter += 1
            else:
                for file in path.glob(REGEXP.PATH_PYTHON):
                    runner.with_file(file)
                    counter += 1
        print(f"Convert {counter} files done.")

    if args.subcommand == "rule":
        if args.show:
            rules = build_in_rules()
            print(f"Total {len(rules)} rules:\n")
            for rule in rules:
                print(rule.relative_to(path_rule))


if __name__ == "__main__":
    raise SystemExit(main())
