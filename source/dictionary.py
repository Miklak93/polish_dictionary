import json
from contextlib import contextmanager
from . import pathmanager
from .convert import Convert
from .fetch import Fetch
from .filter import Filters
from .parse import Parse
from .build import Build
from .constants import (
    DataDir,
    TmpDir,
    DictionaryPath,
    EngUrl,
    PlUrl,
)
from .exception import WikitionaryReaderException
from .record import Record


@contextmanager
def make_context():
    try:
        yield
    except KeyboardInterrupt:
        raise
    finally:
        pathmanager.remove_dir(TmpDir)


class Dictionary:
    def make(
        self,
        include_redirects: bool = False,
        progress_every: int = 10000,
    ):
        pathmanager.ensure_dir(path=DataDir, clean=True)
        pathmanager.ensure_dir(path=TmpDir, clean=True)

        context: dict = {}
        try:
            with make_context():
                context = Fetch(context={"eng": EngUrl, "pl": PlUrl})()
                context = Convert(
                    include_redirects=include_redirects,
                    progress_every=progress_every,
                    context=context,
                )()
                context = Parse(progress_every=progress_every, context=context)()
                Build(progress_every=progress_every, context=context)()
        except KeyboardInterrupt:
            raise

    def search(self, filters: Filters) -> list[Record]:
        if not DictionaryPath.exists():
            raise WikitionaryReaderException(
                f"Dictionary file not found at: {DictionaryPath}. Run 'make' first."
            )

        with open(DictionaryPath, "r", encoding="utf-8") as f:
            data = json.load(f)

        results: list[Record] = []

        for _, entry in data.items():
            record = Record(
                word=entry["word"],
                pos=entry.get("pos", []),
                syllables=entry.get("syllables", {"text": "", "count": 0}),
            )
            if filters.apply(record):
                results.append(record)

        return results