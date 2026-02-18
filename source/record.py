from typing import TypedDict


class Record(TypedDict):
    word: str
    pos: list[str]
    syllables: int
