import logging
import sys
from enum import Enum


class Category(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    PROGRESS = "PROGRESS"
    COMPLETE = "COMPLETE"


class CategoryFormatter(logging.Formatter):
    def __init__(self, fmt: str):
        super().__init__(fmt)
        self._reset = "\x1b[0m"
        self._yellow = "\x1b[33m"
        self._green = "\x1b[32m"

    def format(self, record: logging.LogRecord) -> str:
        category = getattr(record, "category", record.levelname)
        record.category = category

        color = ""
        if category == Category.PROGRESS.value:
            color = self._yellow
        elif category == Category.COMPLETE.value:
            color = self._green

        msg = super().format(record)
        return f"{color}{msg}{self._reset}" if color else msg


class ProgressHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        if getattr(record, "category", "") == Category.PROGRESS.value:
            self.stream.write(msg + "\n")
        else:
            self.stream.write(msg + "\n")
        self.flush()


class Log:
    def __init__(self, name: str = "Logger"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        formatter = CategoryFormatter("%(message)s")

        handler = ProgressHandler(sys.stdout)
        handler.setFormatter(formatter)

        if not self._logger.handlers:
            self._logger.addHandler(handler)

    def error(self, message: str):
        self._logger.error(message, extra={"category": Category.ERROR.value})

    def info(self, message: str):
        self._logger.info(message, extra={"category": Category.INFO.value})

    def progress_pages(self, total: int, written: int, threshold: int = None):
        if threshold is None or (total % threshold == 0):
            self._logger.info(
                f"{self._logger.name}: pages={total} written={written}",
                extra={"category": Category.PROGRESS.value},
            )

    def progress_download(
        self, total: float, downloaded: float, threshold: float = None
    ):
        if threshold is None or (total % threshold == 0):
            self._logger.info(
                f"{self._logger.name}: downloaded={downloaded:.2f}MB total={total:.2f}MB",
                extra={"category": Category.PROGRESS.value},
            )

    def complete_pages(self, total: int, written: int):
        sys.stdout.write("\n")
        self._logger.info(
            f"{self._logger.name} completed: pages={total} written={written}",
            extra={"category": Category.COMPLETE.value},
        )

    def complete_download(self, total: float):
        sys.stdout.write("\n")
        self._logger.info(
            f"{self._logger.name} completed: downloaded={total:.2f}MB",
            extra={"category": Category.COMPLETE.value},
        )
