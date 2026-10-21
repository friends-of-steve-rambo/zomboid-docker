#!/usr/bin/env python3
"""Скачивает все Workshop-моды из mods.yaml через SteamCMD."""

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "mods-download"

mods = yaml.safe_load((ROOT / "mods.yaml").read_text(encoding="utf-8"))["mods"]

if shutil.which("steamcmd") is None:
    sys.exit("steamcmd не найден в PATH")

command = ["steamcmd", "+force_install_dir", str(DEST), "+login", "anonymous"]
for mod in mods:
    workshop_id = str(mod["workshop_id"])
    print(f"{workshop_id} — {mod['name']}", flush=True)
    command += ["+workshop_download_item", "108600", workshop_id, "validate"]
command.append("+quit")

DEST.mkdir(parents=True, exist_ok=True)
result = subprocess.run(command)
if result.returncode != 0:
    sys.exit(f"SteamCMD завершился с кодом {result.returncode}. Запустите скрипт ещё раз.")

content = DEST / "steamapps" / "workshop" / "content" / "108600"
missing = [
    str(mod["workshop_id"])
    for mod in mods
    if not (content / str(mod["workshop_id"])).is_dir()
]
if missing:
    sys.exit(f"Не скачаны: {', '.join(missing)}. Запустите скрипт ещё раз.")

print(f"\nГотово: {content}")
