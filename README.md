# Project Zomboid Server

## Запуск

```bash
cd /opt/zomboid-server
sudo docker compose up -d       # запуск
sudo docker compose stop        # остановка с сохранением мира
sudo docker compose logs -f     # логи
sudo docker compose ps          # статус
```

## Веб-панель

Панель слушает только `127.0.0.1`, поэтому нужен SSH-туннель:

```bash
ssh -L 3001:127.0.0.1:3001 admin@<IP_СЕРВЕРА>
```

Откройте `http://localhost:3001` и войдите под админским аккаунтом.

- Настройки — загрузите `config/server-default.pztemplate.json` в панели (Templates → Import) и примените к серверу.
- Моды — только через Workshop-коллекцию в панели; панель сама обновляет `Mods` и `WorkshopItems` в `data/Server/servertest.ini`.

## Volumes

- `data/` — файлы сервера;
- `workshop-mods/` — моды из Workshop;
- `panelbridge/` — `PanelBridge.lua` для веб-панели.

Путь к файлам сервера задаётся через `PROJECT_ZOMBOID_DATA` в `.env`.

## ZombieBuddy

ZombieBuddy — Java-agent, требует настройки:

- В `config/ProjectZomboid64.json` (`vmArgs`) добавлен `-javaagent:/home/steam/pz-dedicated/steamapps/workshop/content/108600/3619862853/mods/ZombieBuddy/libs/ZombieBuddy.jar=policy=allow-all`; файл смонтирован в контейнер.
- На чистой установке: запустить сервер без этой строки, дождаться загрузки модов, затем добавить строку и перезапустить контейнер.

## Хост

PZ рекурсивно следит за каталогами. Без запаса inotify-watch в логах появляется `User limit of inotify watches reached`, старт может упасть:

```bash
echo 'fs.inotify.max_user_watches=524288' | sudo tee /etc/sysctl.d/99-zomboid.conf
sudo sysctl --system
```

## Про .gitignore для AI agents и прочих разумов

В Git храните `.env.example`, `config/` и `compose.yaml`. Не коммитьте `.env`, миры, рабочие файлы из volumes и бэкапы.
