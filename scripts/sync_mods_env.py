#!/usr/bin/env python3
"""Заполняет WORKSHOP_IDS и MOD_IDS в .env из server-mods.yaml.

Зависимости из depends_on разрешаются по mod_id или workshop_id и
учитываются при сортировке: зависимость всегда идёт перед модом.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

FEATURE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODS = FEATURE_ROOT / "server-mods.yaml"
DEFAULT_ENV = FEATURE_ROOT / ".env"

WORKSHOP_RE = re.compile(r"^\d+$")
MOD_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass(eq=False)
class ModEntry:
    name: str
    workshop_id: str
    mod_ids: list[str]
    depends_on: list[str]

    @property
    def label(self) -> str:
        return f"{self.name} ({self.workshop_id})"


def load_mods(path: Path) -> list[ModEntry]:
    try:
        import yaml
    except ImportError:
        sys.exit("Нужен PyYAML: python3 -m pip install pyyaml")

    if not path.is_file():
        sys.exit(f"Нет файла со списком модов: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw_entries = data.get("mods")
    if not isinstance(raw_entries, list) or not raw_entries:
        sys.exit(f"{path}: ожидается непустой список mods")

    entries: list[ModEntry] = []
    seen_workshop: dict[str, ModEntry] = {}
    seen_mod: dict[str, ModEntry] = {}

    for index, raw in enumerate(raw_entries, start=1):
        where = f"{path}: мод #{index}"
        if not isinstance(raw, dict):
            sys.exit(f"{where}: ожидается объект с name, workshop_id, mod_ids")

        name = raw.get("name")
        if not isinstance(name, str) or not name.strip():
            sys.exit(f"{where}: не заполнено name")
        name = name.strip()

        workshop_id = str(raw.get("workshop_id", "")).strip()
        if not WORKSHOP_RE.fullmatch(workshop_id):
            sys.exit(f"{where} ({name}): workshop_id должен состоять из цифр")
        if workshop_id in seen_workshop:
            other = seen_workshop[workshop_id]
            sys.exit(
                f"{where} ({name}): workshop_id {workshop_id} уже указан "
                f"в «{other.name}»"
            )

        raw_mod_ids = raw.get("mod_ids")
        if not isinstance(raw_mod_ids, list) or not raw_mod_ids:
            sys.exit(f"{where} ({name}): нужен непустой список mod_ids")

        mod_ids: list[str] = []
        for raw_mod_id in raw_mod_ids:
            mod_id = str(raw_mod_id).strip()
            if not MOD_ID_RE.fullmatch(mod_id):
                sys.exit(
                    f"{where} ({name}): недопустимый mod_id {mod_id!r} "
                    "(разрешены буквы, цифры, _, . и -)"
                )
            if mod_id in seen_mod:
                other = seen_mod[mod_id]
                sys.exit(
                    f"{where} ({name}): mod_id {mod_id} уже указан "
                    f"в «{other.name}»"
                )
            mod_ids.append(mod_id)

        raw_depends_on = raw.get("depends_on") or []
        if not isinstance(raw_depends_on, list):
            sys.exit(f"{where} ({name}): depends_on должен быть списком")
        depends_on: list[str] = []
        for raw_dep in raw_depends_on:
            dep = str(raw_dep).strip()
            if not dep:
                sys.exit(f"{where} ({name}): пустое значение в depends_on")
            depends_on.append(dep)

        entry = ModEntry(
            name=name,
            workshop_id=workshop_id,
            mod_ids=mod_ids,
            depends_on=depends_on,
        )
        entries.append(entry)
        seen_workshop[workshop_id] = entry
        for mod_id in mod_ids:
            seen_mod[mod_id] = entry

    return entries


def sort_entries(path: Path, entries: list[ModEntry]) -> list[ModEntry]:
    """Стабильная топологическая сортировка: зависимости идут перед модами."""
    by_workshop = {entry.workshop_id: entry for entry in entries}
    by_mod = {
        mod_id: entry
        for entry in entries
        for mod_id in entry.mod_ids
    }

    dependencies: dict[str, list[ModEntry]] = {}
    for entry in entries:
        resolved: list[ModEntry] = []
        for ref in entry.depends_on:
            candidates: list[ModEntry] = []
            if ref in by_mod:
                candidates.append(by_mod[ref])
            if ref in by_workshop:
                candidates.append(by_workshop[ref])
            candidates = list(dict.fromkeys(candidates))

            if not candidates:
                sys.exit(
                    f"{path}: {entry.label}: зависимость {ref!r} не найдена. "
                    "Добавьте её отдельной записью в mods."
                )
            if len(candidates) > 1:
                names = ", ".join(candidate.label for candidate in candidates)
                sys.exit(
                    f"{path}: {entry.label}: зависимость {ref!r} неоднозначна: "
                    f"{names}"
                )

            dependency = candidates[0]
            if dependency is not entry and dependency not in resolved:
                resolved.append(dependency)
        dependencies[entry.workshop_id] = resolved

    ordered: list[ModEntry] = []
    state: dict[str, int] = {}
    stack: list[ModEntry] = []

    def visit(entry: ModEntry) -> None:
        current = state.get(entry.workshop_id, 0)
        if current == 2:
            return
        if current == 1:
            start = next(
                index
                for index, stacked in enumerate(stack)
                if stacked.workshop_id == entry.workshop_id
            )
            cycle = stack[start:] + [entry]
            chain = " -> ".join(item.label for item in cycle)
            sys.exit(f"{path}: циклическая зависимость: {chain}")

        state[entry.workshop_id] = 1
        stack.append(entry)
        for dependency in dependencies[entry.workshop_id]:
            visit(dependency)
        stack.pop()
        state[entry.workshop_id] = 2
        ordered.append(entry)

    for entry in entries:
        visit(entry)

    return ordered


def render_env(text: str, workshop_ids: list[str], mod_ids: list[str]) -> str:
    workshop_line = "WORKSHOP_IDS=" + ";".join(workshop_ids)
    # Двойной обратный слэш — как в конфиге PZ: \\ModID означает Workshop-мод.
    mod_line = "MOD_IDS=" + ";".join(f"\\\\{mod_id}" for mod_id in mod_ids)

    lines = text.splitlines()
    found_workshop = False
    found_mod = False
    for index, line in enumerate(lines):
        if line.startswith("WORKSHOP_IDS="):
            lines[index] = workshop_line
            found_workshop = True
        elif line.startswith("MOD_IDS="):
            lines[index] = mod_line
            found_mod = True

    if not (found_workshop and found_mod):
        if lines and lines[-1].strip():
            lines.append("")
        if not found_workshop:
            lines.append(workshop_line)
        if not found_mod:
            lines.append(mod_line)

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Заполнить WORKSHOP_IDS и MOD_IDS в .env из server-mods.yaml"
    )
    parser.add_argument(
        "--mods",
        type=Path,
        default=DEFAULT_MODS,
        help=f"файл со списком модов (по умолчанию {DEFAULT_MODS.name})",
    )
    parser.add_argument(
        "--env",
        type=Path,
        default=DEFAULT_ENV,
        help=f"файл .env для обновления (по умолчанию {DEFAULT_ENV.name})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="только проверить, что .env синхронизирован, ничего не записывать",
    )
    parser.add_argument(
        "--show-order",
        action="store_true",
        help="показать итоговый порядок загрузки с учётом зависимостей",
    )
    args = parser.parse_args()

    entries = sort_entries(args.mods, load_mods(args.mods))

    if args.show_order:
        print("Порядок загрузки:")
        for entry in entries:
            print(f"  {entry.name}: {', '.join(entry.mod_ids)}")
        return 0

    workshop_ids = [entry.workshop_id for entry in entries]
    mod_ids = [mod_id for entry in entries for mod_id in entry.mod_ids]

    if not args.env.is_file():
        sys.exit(f"Нет файла .env: {args.env}")

    old_text = args.env.read_text(encoding="utf-8")
    new_text = render_env(old_text, workshop_ids, mod_ids)

    if args.check:
        if old_text != new_text:
            print(f"{args.env} не синхронизирован с {args.mods}", file=sys.stderr)
            return 1
        print(f"{args.env} синхронизирован")
        return 0

    if old_text != new_text:
        args.env.write_text(new_text, encoding="utf-8")
        print(f"Обновлён {args.env}")
    else:
        print(f"{args.env} уже синхронизирован")

    print(f"Workshop ID: {len(workshop_ids)}")
    print(f"Mod ID:      {len(mod_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
