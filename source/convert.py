import bz2
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from .constants import TmpDir
from .exception import WikitionaryReaderException
from .logger import Log
from .parallelrun import ParallelRun


def get_first(page_element: ET.Element, localname: str) -> str:
    for item in page_element.iter():
        if item.tag.endswith(localname):
            return item.text or ""
    return ""


def has_redirect(page_element: ET.Element) -> bool:
    for item in page_element.iter():
        if item.tag.endswith("redirect"):
            return True
    return False


def iter_pages(xml_stream: bz2.BZ2File):
    context = ET.iterparse(xml_stream, events=("end",))
    for _, item in context:
        if item.tag.endswith("page"):
            yield item
            item.clear()


class ConvertEng:
    _pattern = re.compile(r"^==\s*Polish\s*==\s*$", re.IGNORECASE | re.MULTILINE)

    def __init__(self, source_path: Path, include_redirects: bool, progress_every: int):
        self._source_path = source_path
        self._include_redirects = include_redirects
        self._progress_every = progress_every
        self._log = Log("Convert ENG")

    def _page_to_json(self, page: ET.Element) -> dict:
        if get_first(page, "ns") != "0":
            return {}
        if not self._include_redirects and has_redirect(page):
            return {}
        title = get_first(page, "title")
        text = get_first(page, "text")
        if not title or not text:
            return {}
        if not self._pattern.search(text):
            return {}
        return {"title": title, "text": text}

    def __call__(self) -> Path:
        output_path = TmpDir / "eng.converted.json"
        total = 0
        written = 0
        with bz2.open(self._source_path, "rb") as input_file, open(output_path, "w", encoding="utf-8") as out_file:
            for page in iter_pages(input_file):
                total += 1
                result = self._page_to_json(page)
                if result:
                    out_file.write(json.dumps(result, ensure_ascii=False) + "\n")
                    written += 1
                if self._progress_every and total % self._progress_every == 0:
                    self._log.progress_pages(total, written, threshold=None)
        self._log.complete_pages(total, written)
        return output_path


class ConvertPl:
    _pattern = re.compile(
        r"^==\s*[^=\n]+?\s*\(\s*\{\{\s*język\s+polski\s*\}\}\s*\)\s*==\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    def __init__(self, source_path: Path, include_redirects: bool, progress_every: int):
        self._source_path = source_path
        self._include_redirects = include_redirects
        self._progress_every = progress_every
        self._log = Log("Convert PL")

    def _page_to_json(self, page: ET.Element) -> dict:
        if get_first(page, "ns") != "0":
            return {}
        if not self._include_redirects and has_redirect(page):
            return {}
        title = get_first(page, "title")
        text = get_first(page, "text")
        if not title or not text:
            return {}
        if not self._pattern.search(text):
            return {}
        return {"title": title, "text": text}

    def __call__(self) -> Path:
        output_path = TmpDir / "pl.converted.json"
        total = 0
        written = 0
        with bz2.open(self._source_path, "rb") as input_file, open(output_path, "w", encoding="utf-8") as out_file:
            for page in iter_pages(input_file):
                total += 1
                result = self._page_to_json(page)
                if result:
                    out_file.write(json.dumps(result, ensure_ascii=False) + "\n")
                    written += 1
                if self._progress_every and total % self._progress_every == 0:
                    self._log.progress_pages(total, written, threshold=None)
        self._log.complete_pages(total, written)
        return output_path

class Convert(ParallelRun[Path]):
    def __init__(self, context: dict[str, Path], include_redirects: bool, progress_every: int = 10000):
        sources = context.get("fetch", {})
        if "eng" not in sources or "pl" not in sources:
            raise WikitionaryReaderException("Convert requires 'eng' and 'pl' sources.")

        tasks = {
            "eng": ConvertEng(sources["eng"], include_redirects, progress_every),
            "pl": ConvertPl(sources["pl"], include_redirects, progress_every),
        }
        super().__init__(tasks)

    def __call__(self) -> dict:
        return {"convert": super().__call__()}