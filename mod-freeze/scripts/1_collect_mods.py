#!/usr/bin/env python3
"""Собирает скачанные Workshop-моды в плоский каталог mod-freeze/client/."""

import argparse
import shutil
import sys
from pathlib import Path

FEATURE_ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD = FEATURE_ROOT / "download"
SOURCE = DOWNLOAD / "steamapps" / "workshop" / "content" / "108600"
DEST = FEATURE_ROOT / "client"


def is_mod_folder(path: Path) -> bool:
    """Папка мода: mod.info в корне или в common/42/41."""
    if (path / "mod.info").is_file():
        return True
    return any(
        child.is_dir() and (child / "mod.info").is_file()
        for child in path.iterdir()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Собрать моды в mod-freeze/client/")
    parser.add_argument(
        "--keep",
        action="store_true",
        help="не удалять исходный каталог mod-freeze/download/",
    )
    args = parser.parse_args()

    if not SOURCE.is_dir():
        sys.exit(f"Нет скачанных модов: {SOURCE}")

    mod_dirs: list[Path] = []
    for item_dir in sorted(SOURCE.iterdir()):
        mods_dir = item_dir / "mods"
        if not mods_dir.is_dir():
            continue
        for mod_dir in sorted(mods_dir.iterdir()):
            if mod_dir.is_dir() and is_mod_folder(mod_dir):
                mod_dirs.append(mod_dir)

    if not mod_dirs:
        sys.exit("Не найдено ни одной папки мода с mod.info")

    names = [path.name for path in mod_dirs]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        sys.exit(f"Одинаковые имена папок модов: {', '.join(duplicates)}")

    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)

    for mod_dir in mod_dirs:
        shutil.copytree(mod_dir, DEST / mod_dir.name)
        print(f"  {mod_dir.name}")

    print(f"\nСкопировано модов: {len(mod_dirs)}")
    print(f"Готово: {DEST}")

    if not args.keep:
        shutil.rmtree(DOWNLOAD)
        print("Исходный каталог mod-freeze/download/ удалён")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
