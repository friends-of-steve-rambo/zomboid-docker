# Project Zomboid Server

```bash
cd /opt/zomboid-server
sudo docker compose up -d       # запуск
sudo docker compose stop        # остановка с сохранением мира
sudo docker compose logs -f     # логи
sudo docker compose ps          # статус
```

## Миры

- `data/` — тестовый мир.
- `data-friends/` — основной мир.
- `workshop-mods/` — общие моды Workshop.

Активный мир задаётся через `PROJECT_ZOMBOID_DATA` в `.env`. Перед переключением останови сервер.

## Настройки

Редактируй `config/servertest.ini` и `config/servertest_SandboxVars.lua`. После изменений скопируй их в папку активного мира:

```bash
# Остановить сервер
sudo docker compose stop

# Тестовый мир (для основного замени data на data-friends)
cp config/servertest.ini data/Server/
cp config/servertest_SandboxVars.lua data/Server/

# Запустить сервер
sudo docker compose up -d
```

В Git храни `config/` и Compose-файлы. Не добавляй `.env`, миры, моды и бэкапы. Перед изменением настроек основного мира сделай бэкап.
