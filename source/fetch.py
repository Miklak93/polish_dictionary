import urllib.request
from pathlib import Path
from . import pathmanager
from .constants import TmpDir, DataDir
from .exception import WikitionaryReaderException
from .logger import Log
from .parallelrun import ParallelRun


class FetchDump:
    def __init__(self, url: str, name: str):
        self._url = url
        self._log = Log(name)

    def __call__(self) -> Path:
        filename = pathmanager.get_filename(self._url)
        target_path = TmpDir / filename

        try:
            self._log.info(f"Downloading: {self._url} to {target_path}")

            def reporthook(blocknum: int, blocksize: int, totalsize: int):
                if totalsize <= 0:
                    return
                downloaded = (blocknum * blocksize) / (1024 * 1024)
                total = totalsize / (1024 * 1024)
                self._log.progress_download(total=total, downloaded=downloaded, threshold=None)

            urllib.request.urlretrieve(self._url, target_path, reporthook=reporthook)

            self._log.complete_download(target_path.stat().st_size / (1024 * 1024))
            return target_path
        except Exception as e:
            raise WikitionaryReaderException(f"Failed to download dump: {e}") from e

class Fetch(ParallelRun[Path]):
    def __init__(self, context: dict[str, str]):
        pathmanager.ensure_dir(path=DataDir, clean=False)
        tasks = {key: FetchDump(url=url, name=f"Fetch {key.upper()} Dump") for key, url in context.items()}
        super().__init__(tasks)

    def __call__(self) -> dict:
        return {"fetch": super().__call__()}