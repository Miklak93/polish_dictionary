from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class ParallelRun(Generic[T]):
    def __init__(self, tasks: dict[str, Callable[[], T]]):
        if not tasks:
            raise ValueError("ParallelRun tasks cannot be empty.")
        self._tasks = tasks

    def __call__(self) -> dict[str, T]:
        results: dict[str, T] = {}
        with ThreadPoolExecutor(max_workers=len(self._tasks)) as executor:
            futures = {executor.submit(task): key for key, task in self._tasks.items()}
            for future in as_completed(futures):
                key = futures[future]
                results[key] = future.result()
        return results