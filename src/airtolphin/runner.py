from pathlib import Path

import libcst as cst

from airtolphin.constants import KEYWORD
from airtolphin.core.transformer.route import Transformer
from airtolphin.utils.file import add_stem_suffix, read, write


def run(path: Path) -> None:
    content = read(path)
    parse_cst = cst.parse_module(content)
    wrapper = cst.MetadataWrapper(parse_cst)
    converted = wrapper.visit(Transformer()).code

    new_path = add_stem_suffix(path, KEYWORD.CONVERT_MARK)
    write(new_path, converted)
