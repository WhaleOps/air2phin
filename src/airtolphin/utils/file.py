from pathlib import Path
from typing import Any, Dict, List

import yaml


def read(path: Path) -> str:
    with open(path, "r") as f:
        return f.read()


def write(path: Path, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def read_yaml(path: Path) -> Dict[str, Any]:
    assert path.is_file(), "Path must be a single file."
    content = read(path)
    return yaml.safe_load(content)


def read_multi_yaml(paths: List[Path]) -> List[Dict[str, Any]]:
    yamls = []
    for path in paths:
        content = read_yaml(path)
        yamls.append(content)
    return yamls


def add_stem_suffix(path: Path, suf: str) -> Path:
    stem, suffix = path.stem, path.suffix
    new_name = f"{stem}{suf}{suffix}"
    return path.with_name(new_name)
