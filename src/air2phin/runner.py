import logging
import multiprocessing
from multiprocessing import Pool
from pathlib import Path
from timeit import default_timer as timer
from typing import List, Optional

import libcst as cst
from tqdm import tqdm

from air2phin.constants import Keyword, Token
from air2phin.core.rules.config import Config
from air2phin.core.transformer.route import Transformer
from air2phin.utils.file import add_stem_suffix, read, write

logger = logging.getLogger("air2phin.runner")


class Runner:
    """Air2phin runner, main class to run transformer.

    :param config: Config of air2phin.
    """

    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def with_str(self, content: str) -> str:
        """Run air2phin with a string and return migrated content.

        :param content: Content of string you want to migrate.
        """
        parse_cst = cst.parse_module(content)
        wrapper = cst.MetadataWrapper(parse_cst)
        migrated = wrapper.visit(Transformer(self.config)).code
        return migrated

    def with_file(self, path: Path) -> None:
        """Run air2phin with a single file path and migrate to dolphinscheduler python sdk definition.

        Will change file inplace when ``config.inplace = True``, and create new file end with ``-air2phin``
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
            new_path = add_stem_suffix(path, Keyword.MIGRATE_MARK)
            write(new_path, migrated)

        logger.debug("End migrate file %s, elapsed time %.5fs", path, timer() - start)

    def with_files(self, paths: List[Path]) -> None:
        """Run air2phin with multiple files to dolphinscheduler python sdk definition.

        :param paths: Path of file you want to migrate.
        """
        logger.info("Start migrate files, total %d files scan.", len(paths))
        logger.debug(
            "Start migrate files, files contain:\n%s",
            Token.NEW_LINE.join((f"  {p}" for p in paths)),
        )

        start = timer()
        for file in tqdm(paths):
            self.with_file(file)

        logger.info(
            f"Total migrated {len(paths)} files, spend time: %.5fs.", timer() - start
        )

    def with_files_multiprocess(
        self, paths: List[Path], processes: Optional[int] = multiprocessing.cpu_count()
    ) -> None:
        """Run air2phin migrating with multiprocess.

        :param paths: Path of file you want to migrate.
        :param processes: multiprocess processes cpu count number.
        """
        logger.info(
            "Start multiple processing migrate files, total %d files scan.", len(paths)
        )
        logger.debug(
            "Start migrate files with processes number %d, files contain:\n%s",
            processes,
            Token.NEW_LINE.join((f"  {p}" for p in paths)),
        )

        start = timer()
        with Pool(processes) as pool:
            list(tqdm(pool.imap(self.with_file, paths), total=len(paths)))

        logger.debug(
            "All files had add to multiprocess pool, spend time %.5fs.", timer() - start
        )
        pool.join()

        logger.info(
            f"Total migrated {len(paths)} files, spend time: %.5fs.", timer() - start
        )
