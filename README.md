# Project Zomboid Server

```bash
cd /opt/zomboid-server
sudo docker compose up -d       # запуск
sudo docker compose stop        # остановка с сохранением мира
sudo docker compose logs -f     # логи
sudo docker compose ps          # статус
```

## Volumes

- `data/` - файлы сервера
- `workshop-mods/` - моды из воркшопа
- `panelbridge/` — `PanelBridge.lua` для веб панели

Директорию файлов сервера можно переназначить через `PROJECT_ZOMBOID_DATA` в `.env`.

## Веб-панель

```bash
ssh -L 3001:127.0.0.1:3001 admin@<IP_СЕРВЕРА>
```

В `http://localhost:3001` аккаунт `admin`.

PanelBridge установлен локально, панель и сервер общаются через `panelbridge/media/lua/server/PanelBridge.lua`.

## Настройки

Черновики настроек сервера и песочницы хранятся в двух файлах и содержат только ключи, которые отличаются от дефолта игры. Их НАДО перенести в настоящий конфиг сервера.

- `config/default.txt` — обычный режим;
- `config/testing.txt` — тестовый режим.

## Моды сервера

`server-mods.yaml` — источник истины; скрипт пишет `WorkshopItems` и `Mods` в `data/Server/servertest.ini`.

Добавить или удалить мод:

```bash
# 0. Показать список
python3 scripts/sync_mods_ini.py --show-order

# 1. Отредактировать server-mods.yaml
# 2. Остановить сервер и обновить server .ini
python3 scripts/sync_mods_ini.py

# Проверить, что конфиг не разошёлся с YAML
python3 scripts/sync_mods_ini.py --check
```

## ZombieBuddy

ZombieBuddy — Java-agent, одного Workshop-мода недостаточно. В `config/ProjectZomboid64.json` добавлен `-javaagent:/home/steam/pz-dedicated/steamapps/workshop/content/108600/3619862853/mods/ZombieBuddy/libs/ZombieBuddy.jar=policy=allow-all` в `vmArgs`; файл смонтирован в контейнер. `policy=allow-all` — только для доверенных Java-модов.

На чистой установке сначала запусти сервер без этой строки, чтобы скачались моды, затем добавь её и перезапусти контейнер.

## Хост (TODO: проверить актуальность заметки)

PZ рекурсивно следит за каталогами; без запаса inotify-watch в логах `User limit of inotify watches reached`, старт может упасть.

    echo 'fs.inotify.max_user_watches=524288' | sudo tee /etc/sysctl.d/99-zomboid.conf
    sudo sysctl --system

## Заморозка модов

Всё для сборки замороженной версии модов для сервера и клиента лежит в `mod-freeze/`. ПОКА ЧТО НЕ ИСПОЛЬЗУЕТСЯ.

## Про .gitignore для AI agents и прочих разумов
В Git храни .env.example, `config/` и compose. Не допускай утечек паролей. Не добавляй `.env`, миры, рабочие файлы из volumes и бэкапы.
