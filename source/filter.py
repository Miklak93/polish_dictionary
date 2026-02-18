import re
from abc import ABC, abstractmethod
from typing import Any, Callable
from .exception import WikitionaryReaderException
from .record import Record


class Filter:
    def __init__(self, condition: Callable[[Record], bool]):
        self._condition = condition

    def apply(self, item: Record) -> bool:
        return self._condition(item)


class Filters(ABC):
    def __init__(self, filters: list[Filter] = None):
        self._filters = filters if filters else []

    def add(self, filter: Any):
        if isinstance(filter, Filter) or isinstance(filter, Filters):
            self._filters.append(filter)
        else:
            raise WikitionaryReaderException("Invalid filter type.")

    @abstractmethod
    def apply(self, _: Record) -> bool:
        pass


class AndFilters(Filters):
    def __init__(self, filters: list[Filter] = None):
        super().__init__(filters)

    def apply(self, item: Record) -> bool:
        return all(f.apply(item) for f in self._filters)


class OrFilters(Filters):
    def __init__(self, filters: list[Filter] = None):
        super().__init__(filters)

    def apply(self, item: Record) -> bool:
        return True if not self._filters else any(f.apply(item) for f in self._filters)


class RegexFilter(Filter):
    def __init__(self, pattern: str):
        safe_pattern = pattern.replace("*", ".*")
        try:
            compiled_pattern = re.compile(safe_pattern, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {pattern}") from e

        super().__init__(
            lambda record: bool(compiled_pattern.fullmatch(record["word"]))
        )


class TypeFilter(Filter):
    _type_map = {"rz": "rzeczownik", "cz": "czasownik", "p": "przymiotnik"}

    def __init__(self, target_type: str):
        if target_type not in self._type_map:
            raise WikitionaryReaderException("Invalid POS type.")
        expected = self._type_map[target_type]
        super().__init__(lambda record: expected in record["pos"])


class LetterCountFilter(Filter):
    def __init__(self, min_letters: int = 0, max_letters: int = float("inf")):
        super().__init__(
            lambda record: min_letters <= len(record["word"]) <= max_letters
        )


class SyllablesFilter(Filter):
    def __init__(self, min_syllables: int = 0, max_syllables: int = float("inf")):
        super().__init__(
            lambda record: min_syllables <= int(record["syllables"]) <= max_syllables
        )


def make_filters(
    regex,
    types=None,
    min_letters=None,
    max_letters=None,
    min_syllables=None,
    max_syllables=None,
) -> AndFilters:
    filters = AndFilters()

    if not regex:
        raise WikitionaryReaderException("Regex pattern is required for filtering.")
    filters.add(RegexFilter(pattern=regex))

    if types and isinstance(types, list) and len(types) > 0:
        or_filters = OrFilters()
        for t in set(types):
            or_filters.add(TypeFilter(target_type=t))
        filters.add(or_filters)

    l_letters = min_letters if min_letters is not None else 0
    r_letters = max_letters if max_letters is not None else 100
    filters.add(LetterCountFilter(min_letters=l_letters, max_letters=r_letters))
    l_syllables = min_syllables if min_syllables is not None else 0
    r_syllables = max_syllables if max_syllables is not None else float("inf")
    filters.add(SyllablesFilter(min_syllables=l_syllables, max_syllables=r_syllables))

    return filters
