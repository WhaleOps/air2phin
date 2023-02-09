from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from airphin.constants import REGEXP


def read(path: Path) -> str:
    """Read content from path.

    :param path: Path to read content.
    """
    with open(path, "r") as f:
        return f.read()


def write(path: Path, content: str) -> None:
    """Write content to path.

    The path's content will be overwritten if they are already exists.

    :param path: Path to write content.
    :param content: Content want to write to path.
    """
    with open(path, "w") as f:
        f.write(content)


def read_yaml(path: Path) -> Dict[str, Any]:
    """Read yaml file and return a dict.

    :param path: Path to read content.
    """
    assert path.is_file(), "Path must be a single file."
    content = read(path)
    return yaml.safe_load(content)


def read_multi_yaml(paths: List[Path]) -> List[Dict[str, Any]]:
    """Read multiple yaml files and return a list of dict.

    :param paths: List of paths to read.
    """
    yamls = []
    for path in paths:
        content = read_yaml(path)
        yamls.append(content)
    return yamls


def add_stem_suffix(path: Path, suf: str) -> Path:
    """Add stem suffix of path.

    This function add suffix to stem instead of suffix of path, for example:

    >>> add_stem_suffix(Path("foo/bar/baz.py"), "_test")
    Path("foo/bar/baz_test.py")

    :param path: Path to add suffix.
    :param suf: Suffix want to add to stem.
    """
    stem, suffix = path.stem, path.suffix
    new_name = f"{stem}{suf}{suffix}"
    return path.with_name(new_name)


def recurse_files(
    path: Path, include: Optional[str] = REGEXP.PATH_ALL, exclude: Optional[str] = None
) -> List[Path]:
    """Recurse all match pattern files in path.

    :param path: file or directory path want to recurse.
    :param include: include match pattern in given path, default include all file in directory.
    :param exclude: include match pattern in given path, default None.
    """
    if not path.exists():
        raise ValueError("Path %s does not exist.", path)

    if path.is_file():
        return [path]
    else:
        paths = set(path.rglob(include))
        if exclude:
            paths = paths - set(path.rglob(exclude))
        return [file for file in paths if file.is_file()]
