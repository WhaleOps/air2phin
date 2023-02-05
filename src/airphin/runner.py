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
        """Run airphin with a string and return migrated content.

        :param content: Content of string you want to migrate.
        """
        parse_cst = cst.parse_module(content)
        wrapper = cst.MetadataWrapper(parse_cst)
        migrated = wrapper.visit(Transformer(self.config)).code
        return migrated

    def with_file(self, path: Path) -> None:
        """Run airphin with a single file path and migrate to dolphinscheduler python sdk definition.

        Will change file inplace when ``config.inplace = True``, and create new file end with ``-airphin``
        when ``config.inplace = False``.

        :param path: Path of file you want to migrate.
        """
        logger.debug("Start migrate file %s", path)
        start = timer()
        content = read(path)
        migrated = self.with_str(content)

        if self.config.inplace:
            write(path, migrated)
        else:
            new_path = add_stem_suffix(path, KEYWORD.MIGRATE_MARK)
            write(new_path, migrated)

        logger.debug("End migrate file %s, elapsed time %.5fs", path, timer() - start)

    def with_files(self, paths: List[Path]) -> None:
        """Run airphin with multiple files to dolphinscheduler python sdk definition.

        :param paths: Path of file you want to migrate.
        """
        logger.info("Start migrate files, total %d files scan.", len(paths))
        logger.debug(
            "Start migrate files, files contain:\n%s",
            TOKEN.NEW_LINE.join((f"  {p}" for p in paths)),
        )
        start = timer()
        for file in tqdm(paths):
            self.with_file(file)
        logger.info(
            f"Total migrated {len(paths)} files, spend time: %.5fs.", timer() - start
        )
