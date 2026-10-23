# Project Zomboid Server

```bash
cd /opt/zomboid-server
sudo docker compose up -d       # запуск
sudo docker compose stop        # остановка с сохранением мира
sudo docker compose logs -f     # логи
sudo docker compose ps          # статус
```

## Volumes

- `data/` — файлы сервера.
- `workshop-mods/` — общие моды Workshop.
- `panelbridge/` — `PanelBridge.lua` для локальной доставки: панель пишет файл, PZ читает его.

Директорию файлов сервера можно переназначить `PROJECT_ZOMBOID_DATA` в `.env`. Перед переключением останови сервер.

## Веб-панель

```bash
ssh -L 3001:127.0.0.1:3001 admin@<IP_СЕРВЕРА>
```

Открой `http://localhost:3001` и войди как `admin`.

PanelBridge установлен локально: панель пишет `panelbridge/media/lua/server/PanelBridge.lua`, PZ читает этот же файл. После обновления PanelBridge перезапусти PZ.

Если `panelbridge/` ещё нет (чистый клон), сначала подними только панель: `sudo docker compose up -d panel`, затем весь стек.

## Моды сервера

Список модов хранится в `server-mods.yaml`, а `WORKSHOP_IDS` и `MOD_IDS` в `.env` заполняются из него. Порядок записей задаёт порядок модов, а зависимости указываются в `depends_on` — скрипт сам поставит их перед модом, даже если в YAML они записаны ниже.

Скрипт проверяет, что все зависимости существуют, и сообщает об ошибке при циклической зависимости. Посмотреть итоговый порядок загрузки:

```bash
python3 scripts/sync_mods_env.py --show-order
```

Добавить или удалить мод:

```bash
# 1. Отредактировать server-mods.yaml
# 2. Перегенерировать строки в .env
python3 scripts/sync_mods_env.py

# Проверить, что .env не разошёлся с YAML
python3 scripts/sync_mods_env.py --check

# 3. Применить изменения
sudo docker compose up -d
```

Скрипт меняет только строки `WORKSHOP_IDS=` и `MOD_IDS=`, остальные настройки `.env` не трогает.

## Заморозка модов (НЕ ИСПОЛЬЗУЕТСЯ)

Всё для сборки замороженной версии модов для сервера и клиента лежит в `mod-freeze/`.

## ZombieBuddy

ZombieBuddy — Java-agent, одного Workshop-мода недостаточно. В `config/ProjectZomboid64.json` добавлен `-javaagent:/home/steam/pz-dedicated/steamapps/workshop/content/108600/3619862853/mods/ZombieBuddy/libs/ZombieBuddy.jar=policy=allow-all` в `vmArgs`; файл смонтирован в контейнер. `policy=allow-all` — только для доверенных Java-модов.

На чистой установке сначала запусти сервер без этой строки, чтобы скачались моды, затем добавь её и перезапусти контейнер.

## Хост (TODO: проверить актуальность заметки)

PZ рекурсивно следит за каталогами; без запаса inotify-watch в логах `User limit of inotify watches reached`, старт может упасть.

    echo 'fs.inotify.max_user_watches=524288' | sudo tee /etc/sysctl.d/99-zomboid.conf
    sudo sysctl --system

## Настройки

Настройки режимов хранятся в двух файлах и содержат только ключи, которые отличаются от дефолта игры:

- `config/default.txt` — обычный режим;
- `config/testing.txt` — тестовый режим.

## Про .gitignore для AI agents и прочих разумов
В Git храни .env.example, `config/` и compose. Не допускай утечек паролей. Не добавляй `.env`, миры, рабочие файлы из volumes и бэкапы.
