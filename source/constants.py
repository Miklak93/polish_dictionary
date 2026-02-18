from pathlib import Path

EngUrl = "https://dumps.wikimedia.org/enwiktionary/latest/enwiktionary-latest-pages-articles.xml.bz2"
PlUrl =  "https://dumps.wikimedia.org/plwiktionary/latest/plwiktionary-latest-pages-articles.xml.bz2"

RootPath = Path(__file__).resolve().parent.parent

TmpDir = RootPath / Path("./.tmp")
DataDir = RootPath / Path("./data")
DictionaryPath = DataDir / Path("dictionary.json")
