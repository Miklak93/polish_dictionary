import argparse
from .exception import WikitionaryReaderException


class ArgumentParser:
    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description="Wiktionary Processor & Search Tool"
        )

        subparsers = self._parser.add_subparsers(
            dest="command", required=True, help="Command to execute"
        )

        make_parser = subparsers.add_parser(
            "make", help="Process XML dump to JSON dictionary"
        )
        make_parser.add_argument(
            "-r",
            "--include-redirects",
            action="store_true",
            help="Include redirect pages",
        )
        make_parser.add_argument(
            "-p",
            "--progress-every",
            type=int,
            default=10000,
            help="Progress report interval",
        )

        search_parser = subparsers.add_parser(
            "search", help="Search in generated dictionary"
        )
        search_parser.add_argument(
            "-r",
            "--regex",
            required=True,
            help="Regex pattern (e.g., '.*ąt$'). '*' acts as wildcard.",
        )
        search_parser.add_argument(
            "-t",
            "--types",
            nargs="+",
            choices=["rz", "cz", "p"],
            default=None,
            help="Filter by POS: rz (rzeczownik), cz (czasownik), p (przymiotnik)",
        )
        search_parser.add_argument(
            "-m",
            "--min-letters",
            type=int,
            default=None,
            help="Minimum number of letters",
        )
        search_parser.add_argument(
            "-M",
            "--max-letters",
            type=int,
            default=None,
            help="Maximum number of letters",
        )
        search_parser.add_argument(
            "-s",
            "--min-syllables",
            type=int,
            default=None,
            help="Minimum number of syllables",
        )
        search_parser.add_argument(
            "-S",
            "--max-syllables",
            type=int,
            default=None,
            help="Maximum number of syllables",
        )

    def parse_args(self):
        try:
            return self._parser.parse_args()
        except Exception as e:
            raise WikitionaryReaderException("Error parsing arguments") from e
