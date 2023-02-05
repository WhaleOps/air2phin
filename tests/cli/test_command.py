from typing import Dict, List

import pytest

from airphin.cli.command import build_argparse


@pytest.mark.parametrize(
    "argv, expect",
    [
        (
            ["convert", "file"],
            {
                "subcommand": "convert",
                "inplace": False,
            },
        ),
        (
            ["convert", "--inplace", "file"],
            {
                "subcommand": "convert",
                "inplace": True,
            },
        ),
    ],
)
def test_command_args(argv: List[str], expect: Dict):
    parser = build_argparse()
    args = parser.parse_args(argv)
    assert all(val == getattr(args, key) for key, val in expect.items())
