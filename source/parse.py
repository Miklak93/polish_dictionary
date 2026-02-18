import json
import re
import mwparserfromhell
from pathlib import Path
from source.constants import TmpDir
from source.exception import WikitionaryReaderException
from source.logger import Log
from source.parallelrun import ParallelRun


def get_record(value: str) -> dict:
    value = value.strip()
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


def has_multiword_title(record: dict) -> bool:
    title = (record.get("title") or "").strip()
    return not title or len(title.split()) != 1


def is_suffix_or_prefix(record: dict) -> bool:
    title = (record.get("title") or "").strip()
    return title.startswith("-") or title.endswith("-")


def count_syllables_heuristic(word: str) -> int:
    w = word.lower()
    vowels = "aąeęiouóy"
    w = re.sub(rf"i(?=[{vowels}])", "", w)
    return max(len(re.findall(rf"[{vowels}]+", w)), 1)


class ParsePl:
    def __init__(self, converted_path: Path, progress_every: int = 10000):
        self._converted_path = converted_path
        self._progress_every = progress_every
        self._log = Log("Parse PL")

    def _clean_wikicode_value(self, value_obj) -> list[str]:
        raw_value = str(value_obj)
        raw_value = re.sub(r"<ref.*?>.*?</ref>", "", raw_value, flags=re.DOTALL)
        raw_value = re.sub(r"<ref.*?/>", "", raw_value)
        parsed = mwparserfromhell.parse(raw_value).strip_code()
        parsed = re.sub(r"\(.*?\)", "", parsed)
        parts = parsed.split("/")
        valid_forms = []
        for part in parts:
            cleaned = part.strip()
            if not cleaned:
                continue
            if cleaned.lower() in ["brak", "–", "-", "—"]:
                continue
            if not re.search(r"[a-zA-ZąęćłńóśźżĄĘĆŁŃÓŚŹŻ]", cleaned):
                continue
            valid_forms.append(cleaned)
        return valid_forms

    def _extract_inflection_and_pos(self, wikicode) -> tuple[dict, str]:
        inflection = {}
        detected_pos = "nieznany"

        templates = wikicode.filter_templates(
            matches=lambda t: str(t.name).strip().startswith("odmiana-")
        )

        if templates:
            main_template = templates[0]
            template_name = str(main_template.name).strip()

            if "rzeczownik" in template_name:
                detected_pos = "rzeczownik"
            elif "czasownik" in template_name:
                detected_pos = "czasownik"
            elif "przymiotnik" in template_name:
                detected_pos = "przymiotnik"
            elif "zaimek" in template_name:
                detected_pos = "zaimek"

            inflection["typ_odmiany"] = template_name

            for param in main_template.params:
                key = str(param.name).strip()
                vals = self._clean_wikicode_value(param.value)
                if vals and key:
                    inflection[key] = vals

        return inflection, detected_pos

    def _process_record(self, record: dict) -> dict:
        if is_suffix_or_prefix(record):
            return {}

        raw_text = record.get("text")
        if not isinstance(raw_text, str) or not raw_text:
            return {}

        try:
            wikicode = mwparserfromhell.parse(raw_text)
        except Exception:
            return {}

        inflection, pos_from_template = self._extract_inflection_and_pos(wikicode)

        final_pos = pos_from_template
        if final_pos == "nieznany":
            sections = wikicode.get_sections(matches="znaczenia")
            if sections:
                txt = str(sections[0])
                if "''rzeczownik" in txt:
                    final_pos = "rzeczownik"
                elif "''czasownik" in txt:
                    final_pos = "czasownik"
                elif "''przymiotnik" in txt:
                    final_pos = "przymiotnik"

        if not inflection and final_pos == "nieznany":
            return {}

        return {
            "title": record["title"],
            "pos": final_pos,
            "inflection": inflection,
        }

    def __call__(self) -> Path:
        output_path = TmpDir / "pl.parsed.json"
        total = 0
        written = 0

        with open(self._converted_path, "r", encoding="utf-8") as input_file, open(
            output_path, "w", encoding="utf-8"
        ) as out_file:
            for line in input_file:
                total += 1
                record = get_record(line)
                if not record:
                    continue
                if has_multiword_title(record):
                    continue

                processed = self._process_record(record)
                if not processed:
                    continue

                out_file.write(json.dumps(processed, ensure_ascii=False) + "\n")
                written += 1

                if self._progress_every and total % self._progress_every == 0:
                    self._log.progress_pages(total, written, threshold=None)

        self._log.complete_pages(total, written)
        return output_path


class ParseEng:
    def __init__(self, converted_path: Path, progress_every: int = 10000):
        self._converted_path = converted_path
        self._progress_every = progress_every
        self._log = Log("Parse ENG")

    def _extract_polish_section(self, text: str) -> str:
        m = re.search(r"(?im)^==\s*Polish\s*==\s*$", text)
        if not m:
            return ""
        start = m.start()
        m2 = re.search(r"(?im)^==\s*[^=].*?\s*==\s*$", text[m.end():])
        end = (m.end() + m2.start()) if m2 else len(text)
        return text[start:end]

    def _extract_pos_list(self, polish_text: str) -> list[str]:
        pos_map = {
            "noun": "rzeczownik",
            "verb": "czasownik",
            "adjective": "przymiotnik",
        }
        found = re.findall(r"(?im)^===\s*([^=\n]+?)\s*===\s*$", polish_text)
        out = []
        for raw in found:
            key = raw.strip().lower()
            if key in pos_map:
                out.append(pos_map[key])
        return sorted(set(out))

    def _process_record(self, record: dict) -> dict:
        if is_suffix_or_prefix(record):
            return {}

        raw_text = record.get("text")
        if not isinstance(raw_text, str) or not raw_text:
            return {}

        title = (record.get("title") or "").strip()
        if not title:
            return {}

        polish_section = self._extract_polish_section(raw_text)
        if not polish_section:
            return {}

        pos = self._extract_pos_list(polish_section)
        if not pos:
            return {}

        syllables = count_syllables_heuristic(title)
        return {"word": title, "pos": pos, "syllables": syllables}

    def __call__(self) -> Path:
        output_path = TmpDir / "eng.parsed.json"
        total = 0
        written = 0

        with open(self._converted_path, "r", encoding="utf-8") as input_file, open(
            output_path, "w", encoding="utf-8"
        ) as out_file:
            for line in input_file:
                total += 1
                record = get_record(line)
                if not record:
                    continue
                if has_multiword_title(record):
                    continue

                processed = self._process_record(record)
                if not processed:
                    continue

                out_file.write(json.dumps(processed, ensure_ascii=False) + "\n")
                written += 1

                if self._progress_every and total % self._progress_every == 0:
                    self._log.progress_pages(total, written, threshold=None)

        self._log.complete_pages(total, written)
        return output_path


class Parse(ParallelRun[Path]):
    def __init__(self, context: dict[str, Path], progress_every: int = 10000):
        converted = context.get("convert", {})
        if "eng" not in converted or "pl" not in converted:
            raise WikitionaryReaderException("Parse requires 'eng' and 'pl' sources.")

        tasks = {
            "pl": ParsePl(converted["pl"], progress_every),
            "eng": ParseEng(converted["eng"], progress_every),
        }
        super().__init__(tasks)

    def __call__(self) -> dict:
        return {"parse": super().__call__()}