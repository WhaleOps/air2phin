import logging
from pathlib import Path
from timeit import default_timer as timer
from typing import List

import libcst as cst
from tqdm import tqdm

from airphin.constants import KEYWORD, TOKEN
from airphin.core.rules.config import Config
from airphin.core.transformer.route import Transformer
from airphin.utils.file import add_stem_suffix, read, write

logger = logging.getLogger("airphin.runner")


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
        """Run airphin with a single file path and convert to dolphinscheduler python sdk definition.

        Will change file inplace when ``config.inplace = True``, and create new file end with ``-airphin``
        when ``config.inplace = False``.

        :param path: Path of file you want to convert.
        """
        content = read(path)
        converted = self.with_str(content)

        logger.debug("Start convert file %s", path)
        start = timer()
        if self.config.inplace:
            write(path, converted)
        else:
            new_path = add_stem_suffix(path, KEYWORD.CONVERT_MARK)
            write(new_path, converted)

        logger.debug("End convert file %s, elapsed time %.5fs", path, timer() - start)

    def with_files(self, paths: List[Path]) -> None:
        """Run airphin with multiple files to dolphinscheduler python sdk definition.

        :param paths: Path of file you want to convert.
        """
        logger.info("Start convert files, total %d files scan.", len(paths))
        logger.debug(
            "Start convert files, files contain:\n%s",
            TOKEN.NEW_LINE.join((f"  {p}" for p in paths)),
        )
        start = timer()
        for file in tqdm(paths):
            self.with_file(file)
        logger.info(
            f"Total converted {len(paths)} files, spend time: %.5fs.", timer() - start
        )
