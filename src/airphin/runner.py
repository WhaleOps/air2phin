from pathlib import Path

import libcst as cst

from airphin.constants import KEYWORD
from airphin.core.rules.config import Config
from airphin.core.transformer.route import Transformer
from airphin.utils.file import add_stem_suffix, read, write


class Runner:
    """Airphin runner, main class to run transformer.

    :param config: Config of airphin.
    """

    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def with_str(self, content: str) -> str:
        """Run airphin with a string and return converted content.

        :param content: Content of string you want to convert.
        """
        parse_cst = cst.parse_module(content)
        wrapper = cst.MetadataWrapper(parse_cst)
        converted = wrapper.visit(Transformer(self.config)).code
        return converted

    def with_file(self, path: Path) -> None:
        """Run airphin with a single file path and create a new file with converted content.

        :param path: Path of file you want to convert.
        """
        content = read(path)
        converted = self.with_str(content)

        new_path = add_stem_suffix(path, KEYWORD.CONVERT_MARK)
        write(new_path, converted)
