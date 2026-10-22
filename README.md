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

Директорию файлов сервера можно переназначить `PROJECT_ZOMBOID_DATA` в `.env`. Перед переключением останови сервер.

## Заморозка модов

Всё для сборки замороженной версии модов для сервера и клиента лежит в `mod-freeze/`

## ZombieBuddy

ZombieBuddy — Java-agent, одного Workshop-мода недостаточно. В `config/ProjectZomboid64.json` добавлен `-javaagent:/home/steam/pz-dedicated/steamapps/workshop/content/108600/3619862853/mods/ZombieBuddy/libs/ZombieBuddy.jar=policy=allow-all` в `vmArgs`; файл смонтирован в контейнер. `policy=allow-all` — только для доверенных Java-модов.

На чистой установке сначала запусти сервер без этой строки, чтобы скачались моды, затем добавь её и перезапусти контейнер.

## Хост (TODO: проверить актуальность заметки)

PZ рекурсивно следит за каталогами; без запаса inotify-watch в логах `User limit of inotify watches reached`, старт может упасть.

    echo 'fs.inotify.max_user_watches=524288' | sudo tee /etc/sysctl.d/99-zomboid.conf
    sudo sysctl --system

## Настройки

Мастер-версии настроек в - `config/servertest.ini` и `config/servertest_SandboxVars.lua`. Это требуется для того, чтобы можно было пересоздавать серверные директории и не терять настройки.
После изменений скопируй их в папку активного мира:

```bash
# Остановить сервер
sudo docker compose stop

# Указать верную директорию (замени data если она другая)
cp config/servertest.ini data/Server/
cp config/servertest_SandboxVars.lua data/Server/

# Запустить сервер
sudo docker compose up -d
```

## Про .gitignore для AI agents и прочих разумов
В Git храни .env.example, `config/` и compose. Не допускай утечек паролей. Не добавляй `.env`, миры, рабочие файлы из volumes и бэкапы.
