import json
from pathlib import Path

from . import pathmanager
from .constants import DictionaryPath
from .exception import WikitionaryReaderException
from .logger import Log
from .parallelrun import ParallelRun


def get_record(value: str) -> dict:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


class BuildLang:
    def __init__(self, parsed_path: Path, name: str, progress_every: int = 10000):
        self._parsed_path = parsed_path
        self._progress_every = progress_every
        self._log = Log(name)

    def __call__(self) -> dict:
        index = {}
        total_read = 0
        with open(self._parsed_path, "r", encoding="utf-8") as f:
            for line in f:
                total_read += 1
                record = get_record(line)
                if not record:
                    continue
                word = (record.get("word") or record.get("title") or "").strip()
                if not word:
                    continue
                key = word.lower()
                pos = record.get("pos", [])
                syllables = int(record.get("syllables", 0))
                index[key] = {"word": word, "pos": pos, "syllables": syllables}
                if self._progress_every and total_read % self._progress_every == 0:
                    self._log.progress_pages(total_read, len(index), threshold=None)
        self._log.complete_pages(total_read, len(index))
        return index

class Build(ParallelRun[dict]):
    def __init__(self, context: dict[str, Path], progress_every: int = 10000):
        parsed = context.get("parse", {})
        if "eng" not in parsed or "pl" not in parsed:
            raise WikitionaryReaderException("Build requires 'eng' and 'pl' sources.")

        pathmanager.ensure_file(DictionaryPath, clean=True)
        self._log = Log("Build dictionary")

        tasks = {
            "eng": BuildLang(parsed["eng"], "Build ENG index", progress_every),
            "pl": BuildLang(parsed["pl"], "Build PL index", progress_every),
        }
        super().__init__(tasks)

    def __call__(self) -> Path:
        parts = super().__call__()
        eng = parts.get("eng", {})
        pl = parts.get("pl", {})

        final_index = dict(eng)
        for k, v in pl.items():
            if k not in final_index:
                final_index[k] = v

        sorted_index = dict(sorted(final_index.items()))
        with open(DictionaryPath, "w", encoding="utf-8") as out_file:
            json.dump(sorted_index, out_file, ensure_ascii=False, indent=0)

        self._log.complete_pages(len(eng) + len(pl), len(sorted_index))
        return DictionaryPath