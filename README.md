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
