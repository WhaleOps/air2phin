import argparse
import difflib
import logging
import sys
from pathlib import Path
from typing import Dict, Sequence

from airphin import __project_name__, __version__
from airphin.constants import REGEXP, TOKEN
from airphin.core.rules.config import Config
from airphin.core.rules.loader import build_in_rules, path_rule
from airphin.runner import Runner
from airphin.utils.file import recurse_files

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("airphin")

common_args: Dict[str, Dict] = {
    "custom_rules": {
        "help": f"The custom rule file path you want to add to {__project_name__}.",
        "action": "append",
        "type": Path,
    },
    "custom_only": {
        "help": "Only use custom rules and ignore all built-in's, it is helpful for patching the"
        "exists migration.",
        "action": "store_true",
    },
    "verbose": {
        "action": "store_true",
        "help": "Show more verbose output.",
    },
}


def build_argparse() -> argparse.ArgumentParser:
    """Build argparse.ArgumentParser with specific configuration."""
    parser = argparse.ArgumentParser(
        prog="airphin",
        description="Airphin is a tool for migrating Airflow DAGs to DolphinScheduler Python API.",
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
    parser_test = subparsers.add_parser(
        "test", help=f"{__project_name__} playground for migrating with standard input."
    )
    parser_test.add_argument(
        "-v",
        "--verbose",
        **common_args["verbose"],
    )
    parser_test.add_argument(
        "-r",
        "--custom-rules",
        **common_args["custom_rules"],
    )
    parser_test.add_argument(
        "-R",
        "--custom-only",
        **common_args["custom_only"],
    )
    parser_test.add_argument(
        "-d",
        "--diff",
        action="store_true",
        help=f"Prints diff of all the changes {__project_name__} would make.",
    )
    parser_test.add_argument(
        "stdin",
        help="The standard input you want to migrate.",
        action="store",
        type=str,
    )

    # migrate
    parser_migrate = subparsers.add_parser(
        "migrate", help="Migrate Airflow DAGs to DolphinScheduler Python definition."
    )
    parser_migrate.add_argument(
        "-v",
        "--verbose",
        **common_args["verbose"],
    )
    parser_migrate.add_argument(
        "-r",
        "--custom-rules",
        **common_args["custom_rules"],
    )
    parser_migrate.add_argument(
        "-R",
        "--custom-only",
        **common_args["custom_only"],
    )
    parser_migrate.add_argument(
        "-I",
        "--include",
        help=f"Include files based on conditions provided, default '{REGEXP.PATH_PYTHON}'",
        action="store",
        default=REGEXP.PATH_PYTHON,
        type=str,
    )
    parser_migrate.add_argument(
        "-E",
        "--exclude",
        help="Exclude files based on conditions provided, without default value",
        action="store",
        type=str,
    )
    parser_migrate.add_argument(
        "-i",
        "--inplace",
        help="Migrate python file in place instead of create a new file.",
        action="store_true",
    )
    parser_migrate.add_argument(
        "-m",
        "--multiprocess",
        help="Migrate python files with multiprocess.",
        action="store",
        type=int,
    )
    parser_migrate.add_argument(
        "sources",
        default=[Path(".")],
        nargs="*",
        help="The directories or files paths you want to migrate.",
        action="store",
        type=Path,
    )

    # Rule
    parser_rule = subparsers.add_parser("rule", help="Rule of migrating.")
    parser_rule.add_argument(
        "-s",
        "--show",
        action="store_true",
        help=f"Show all rules for {__project_name__} migrate.",
    )

    return parser


def main(argv: Sequence[str] = None) -> None:
    """Run airphin in command line."""
    parser = build_argparse()
    argv = argv if argv is not None else sys.argv[1:]
    # argv = ["rule", "--show"]
    args = parser.parse_args(argv)

    if hasattr(args, "verbose") and args.verbose:
        logger.setLevel(logging.DEBUG)
    logger.debug("Finish parse airphin arguments, current args is %s.", args)

    # recurse all file in given path
    customs_rules = []
    if hasattr(args, "custom_rules") and args.custom_rules:
        for rule in args.custom_rules:
            customs_rules.extend(recurse_files(rule))
    if logger.level <= logging.DEBUG and customs_rules:
        logger.debug(
            "This migration have custom rules:\n%s",
            TOKEN.NEW_LINE.join((f"  {r}" for r in customs_rules)),
        )

    if args.subcommand == "test":
        stdin = args.stdin
        config = Config(customs=customs_rules, customs_only=args.custom_only)
        runner = Runner(config)

        result = runner.with_str(stdin)
        logger.debug("The source input is:\n%s", stdin)
        logger.info(f"Migrated result is: \n{result}")

        if args.diff:
            diff = difflib.unified_diff(
                stdin.splitlines(keepends=True),
                result.splitlines(keepends=True),
                fromfile="source",
                tofile="dest",
            )
            logger.info(
                f"The different between source and target is: \n{''.join(diff)}"
            )

    if args.subcommand == "migrate":
        migrate_files = []
        for path in args.sources:
            migrate_files.extend(recurse_files(path, args.include, args.exclude))

        config = Config(
            customs=customs_rules, customs_only=args.custom_only, inplace=args.inplace
        )
        runner = Runner(config)

        if args.multiprocess:
            runner.with_files_multiprocess(migrate_files, args.multiprocess)
        else:
            runner.with_files(migrate_files)

    if args.subcommand == "rule":
        if args.show:
            rules = build_in_rules()
            logger.info(f"Total {len(rules)} rules:\n")
            for rule in rules:
                print(rule.relative_to(path_rule))


if __name__ == "__main__":
    raise SystemExit(main())
