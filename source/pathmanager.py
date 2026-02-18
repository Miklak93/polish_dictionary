import shutil
from pathlib import Path
import urllib.parse


def ensure_dir(path: Path, clean: bool = False):
    if clean and path.exists():
        for item in path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        return

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def remove_dir(path: Path):
    if not path.exists() or not path.is_dir():
        return

    for item in path.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    path.rmdir()


def ensure_file(path: Path, clean: bool = False):
    if clean:
        remove_file(path)
    if not path.exists():
        path.touch()


def remove_file(path: Path):
    if path.exists() and path.is_file():
        path.unlink()

def get_filename(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return Path(parsed.path).name