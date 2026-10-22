#!/usr/bin/env python3
"""Упаковывает mod-freeze/client/ в один zip-архив в mod-freeze/dist/."""

import sys
import zipfile
from datetime import datetime
from pathlib import Path

FEATURE_ROOT = Path(__file__).resolve().parent.parent
SOURCE = FEATURE_ROOT / "client"
DIST = FEATURE_ROOT / "dist"

README = """Project Zomboid — client mods
Собрано: {packed_at}
Модов: {mod_count}

Установка
---------
1. Закройте Project Zomboid.
2. Распакуйте архив в папку Zomboid так, чтобы получилось:
   Zomboid/mods/<Mod>/mod.info
   Windows: %USERPROFILE%\\Zomboid
   Linux:   ~/Zomboid
3. Запустите игру. Если локальные моды не видны, запустите с параметром:
   -modfolders mods
4. Включите моды в меню Mods.
5. Удалите или отпишите старые Workshop-копии этих модов, чтобы не было дублей.

Порядок загрузки
----------------
Сначала базовые моды:
  ZombieBuddy
  Viewpoint
  PZVoxelStudioViewpoint
Затем остальные аддоны.
Если вы играете на сервере, порядок может задаваться серверным Mods=;
в этом случае ориентируйтесь на сервер.

Сервер
------
Эти моды клиентские: серверу они не обязательны.
Для сервера папки модов можно скопировать в data/mods, но это отдельный шаг.
"""


def has_mod_info(path: Path) -> bool:
    if (path / "mod.info").is_file():
        return True
    return any(
        child.is_dir() and (child / "mod.info").is_file()
        for child in path.iterdir()
    )


def main() -> int:
    if not SOURCE.is_dir():
        sys.exit(f"Нет каталога с модами: {SOURCE}")

    mods = sorted(
        path for path in SOURCE.iterdir()
        if path.is_dir() and has_mod_info(path)
    )
    if not mods:
        sys.exit("В mod-freeze/client/ не найдено папок модов с mod.info")

    DIST.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive = DIST / f"zomboid-mods-{timestamp}.zip"

    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
        allowZip64=True,
    ) as zf:
        for mod in mods:
            print(f"  {mod.name}")
            for path in sorted(mod.rglob("*")):
                if path.is_file():
                    zf.write(path, Path("mods") / mod.name / path.relative_to(mod))

        zf.writestr(
            "README.txt",
            README.format(
                packed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                mod_count=len(mods),
            ),
        )

    size_mb = archive.stat().st_size / (1024 * 1024)
    print(f"\nМодов в архиве: {len(mods)}")
    print(f"Архив: {archive}")
    print(f"Размер: {size_mb:.1f} МБ")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
