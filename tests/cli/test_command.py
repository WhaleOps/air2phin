from typing import Dict, List

import pytest

from air2phin.cli.command import build_argparse


@pytest.mark.parametrize(
    "argv, expect",
    [
        (
            ["migrate", "file"],
            {
                "subcommand": "migrate",
                "inplace": False,
            },
        ),
        (
            ["migrate", "--inplace", "file"],
            {
                "subcommand": "migrate",
                "inplace": True,
            },
        ),
    ],
)
def test_command_args(argv: List[str], expect: Dict):
    parser = build_argparse()
    args = parser.parse_args(argv)
    assert all(val == getattr(args, key) for key, val in expect.items())
