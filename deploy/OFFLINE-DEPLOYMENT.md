# Оффлайн-развёртывание OpenLocalSearchParser

Руководство по переносу и запуску платформы на машине **без доступа в интернет** (или с ограниченной сетью). Все Docker-образы упаковываются в `tar.gz`, переносятся на целевой хост и загружаются локально.

---

## Содержание

1. [Обзор](#обзор)
2. [Требования](#требования)
3. [Схема процесса](#схема-процесса)
4. [Этап 1: подготовка на машине с интернетом](#этап-1-подготовка-на-машине-с-интернетом)
5. [Этап 2: перенос файлов](#этап-2-перенос-файлов)
6. [Этап 3: развёртывание на оффлайн-машине](#этап-3-развёртывание-на-оффлайн-машине)
7. [Конфигурация портов](#конфигурация-портов)
8. [Проверка после запуска](#проверка-после-запуска)
9. [Интеграция с Open WebUI](#интеграция-с-open-webui)
10. [Обновление оффлайн-установки](#обновление-оффлайн-установки)
11. [Устранение неполадок](#устранение-неполадок)
12. [Справочник: образы и файлы](#справочник-образы-и-файлы)

---

## Обзор

Оффлайн-развёртывание состоит из трёх этапов:

| Этап | Где выполняется | Действие |
|------|-----------------|----------|
| Экспорт | Машина с интернетом | Сборка и сохранение образов в `deploy/offline/images/*.tar.gz` |
| Перенос | USB / сеть / архив | Копирование образов, конфигов, моделей |
| Импорт и запуск | Оффлайн-машина | `docker load` + `docker compose up --no-build` |

В обычном режиме `docker compose` **собирает** образы из исходников (`build:`). В оффлайн-режиме используется overlay-файл `deploy/docker-compose.offline.yml`, который подставляет **готовые образы** (`image:`) и запрещает пересборку (`--no-build`).

---

## Требования

### Машина для экспорта (с интернетом)

- Docker Desktop или Docker Engine + Docker Compose v2
- NVIDIA GPU и [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) (для сборки и теста llama.cpp CUDA-образа)
- Достаточно места на диске: **15–30 ГБ** (образы + модели)
- Исходный код репозитория
- GGUF-модели в папке `model/` (см. ниже)

### Оффлайн-машина (целевая)

- Docker Desktop или Docker Engine + Docker Compose v2
- NVIDIA GPU и NVIDIA Container Toolkit
- Те же GGUF-модели в `model/`
- Место на диске для образов и данных (PostgreSQL, Qdrant, MinIO)

### Модели (обязательно на обеих машинах)

Положите файлы в каталог `model/` в корне репозитория:

| Файл | Назначение |
|------|------------|
| `GLM-OCR-Q8_0.gguf` | OCR |
| `mmproj-GLM-OCR-Q8_0.gguf` | multimodal projector для OCR |
| `Qwen3-Embedding-0.6B-Q8_0.gguf` | эмбеддинги для поиска |

Модели **не входят** в Docker-образы и **не попадают** в git. Их нужно переносить отдельно.

---

## Схема процесса

```text
[Машина с интернетом]
  │
  ├─ cp .env.example .env
  ├─ cp deploy/ports.example.env deploy/ports.env
  ├─ export-offline-bundle.ps1 / .sh
  │     ├─ docker compose build (backend, worker, frontend)
  │     ├─ docker compose pull (postgres, qdrant, redis, minio, llama.cpp)
  │     └─ docker save → deploy/offline/images/*.tar.gz + manifest.json
  │
  └─ Упаковать и перенести:
        deploy/offline/images/
        deploy/ports.env
        deploy/docker-compose.yml
        deploy/docker-compose.offline.yml
        deploy/scripts/
        .env
        model/

[Оффлайн-машина]
  │
  ├─ import-offline-bundle.ps1 / .sh  (docker load)
  └─ offline-up.ps1 / .sh             (compose up --no-build)
```

---

## Этап 1: подготовка на машине с интернетом

### 1.1. Клонировать репозиторий и настроить окружение

```powershell
# Windows (PowerShell)
cd D:\dev\OpenLocalSearchParser   # путь к репозиторию

cp .env.example .env
cp deploy\ports.example.env deploy\ports.env
```

```bash
# Linux / macOS
cd /path/to/OpenLocalSearchParser

cp .env.example .env
cp deploy/ports.example.env deploy/ports.env
```

При необходимости отредактируйте `.env` (API-ключи Open WebUI и т.д.) и `deploy/ports.env` (порты на хосте).

### 1.2. Положить модели

```text
model/
  GLM-OCR-Q8_0.gguf
  mmproj-GLM-OCR-Q8_0.gguf
  Qwen3-Embedding-0.6B-Q8_0.gguf
```

### 1.3. Экспортировать Docker-образы

**Windows:**

```powershell
.\deploy\scripts\export-offline-bundle.ps1
```

**Linux / macOS:**

```bash
chmod +x deploy/scripts/*.sh
./deploy/scripts/export-offline-bundle.sh
```

Скрипт выполняет:

1. Создаёт `deploy/ports.env`, если его нет
2. Собирает локальные образы: `backend`, `worker`, `frontend`
3. Скачивает сторонние образы: PostgreSQL, Qdrant, Redis, MinIO, llama.cpp CUDA
4. Помечает локальные образы тегами `openlocalsearchparser/*:offline`
5. Сохраняет каждый образ в `deploy/offline/images/<имя>.tar.gz`
6. Записывает `deploy/offline/images/manifest.json`

По завершении в `deploy/offline/images/` должны появиться 8 архивов и `manifest.json`.

### 1.4. (Рекомендуется) Проверить экспорт на той же машине

```powershell
.\deploy\scripts\offline-up.ps1 -ImportImages
```

Если сервисы поднялись — экспорт корректен. Остановите тестовый запуск:

```powershell
docker compose --env-file deploy/ports.env -f deploy/docker-compose.yml -f deploy/docker-compose.offline.yml -p openlocalsearchparser down
```

---

## Этап 2: перенос файлов

Скопируйте на оффлайн-машину **минимальный набор**:

```text
deploy/
  offline/images/          # все *.tar.gz + manifest.json
  ports.env                # или ports.example.env (скопировать в ports.env на месте)
  docker-compose.yml
  docker-compose.offline.yml
  scripts/
    export-offline-bundle.ps1   # опционально
    import-offline-bundle.ps1
    offline-up.ps1
    *.sh                        # для Linux

.env                         # из .env.example, с вашими настройками
model/                       # три GGUF-файла
```

Полный репозиторий переносить **не обязательно**, но удобно для обновлений и документации.

### Варианты переноса

| Способ | Комментарий |
|--------|-------------|
| Внешний диск / USB | Надёжно для больших образов |
| `tar` / `zip` архив | Удобно для одного файла |
| Внутренняя сеть | `scp`, `rsync`, общая папка |
| CI-артефакт | Сохранить `deploy/offline/images/` как артефакт сборки |

Ориентировочный размер только образов (без моделей): **8–15 ГБ**.

---

## Этап 3: развёртывание на оффлайн-машине

### 3.1. Установить Docker и NVIDIA Container Toolkit

Убедитесь, что команды работают:

```bash
docker --version
docker compose version
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

На оффлайн-машине образ `nvidia/cuda` для проверки GPU может отсутствовать — тогда достаточно `nvidia-smi` на хосте и корректной установки Container Toolkit.

### 3.2. Расположить файлы

Структура на целевой машине (пример):

```text
/opt/openlocalsearchparser/
  .env
  model/
  deploy/
    ports.env
    docker-compose.yml
    docker-compose.offline.yml
    offline/images/
    scripts/
```

### 3.3. Настроить конфигурацию

```powershell
# если ports.env ещё нет
cp deploy\ports.example.env deploy\ports.env
```

```bash
cp deploy/ports.example.env deploy/ports.env
```

Проверьте `.env` — он должен существовать (скопируйте с экспортной машины или из `.env.example`).

### 3.4. Импорт образов

**Windows:**

```powershell
cd D:\opt\openlocalsearchparser
.\deploy\scripts\import-offline-bundle.ps1
```

**Linux / macOS:**

```bash
cd /opt/openlocalsearchparser
chmod +x deploy/scripts/*.sh
./deploy/scripts/import-offline-bundle.sh
```

Скрипт читает `manifest.json` (или все `*.tar.gz` в каталоге) и выполняет `docker load` для каждого архива.

Проверка:

```bash
docker images | grep -E "openlocalsearchparser|postgres|qdrant|redis|minio|llama"
```

### 3.5. Запуск сервисов

**Windows:**

```powershell
.\deploy\scripts\offline-up.ps1
```

**Linux / macOS:**

```bash
./deploy/scripts/offline-up.sh
```

Импорт и запуск одной командой:

```powershell
.\deploy\scripts\offline-up.ps1 -ImportImages
```

```bash
./deploy/scripts/offline-up.sh --import
```

Скрипт `offline-up` вызывает:

```text
docker compose
  --env-file deploy/ports.env
  -f deploy/docker-compose.yml
  -f deploy/docker-compose.offline.yml
  -p openlocalsearchparser
  up -d --no-build
```

Флаг `--no-build` гарантирует, что Docker **не попытается** скачать или собрать образы из интернета.

---

## Конфигурация портов

Все **внешние** (host) порты задаются в одном файле: `deploy/ports.env`.

Значения по умолчанию (`deploy/ports.example.env`):

| Переменная | Порт | Сервис |
|------------|------|--------|
| `OLSP_FRONTEND_HOST_PORT` | 18473 | Vue frontend |
| `OLSP_BACKEND_HOST_PORT` | 52891 | FastAPI backend |
| `OLSP_QDRANT_HOST_PORT` | 36144 | Qdrant UI/API |
| `OLSP_MINIO_API_HOST_PORT` | 49280 | MinIO S3 API |
| `OLSP_MINIO_CONSOLE_HOST_PORT` | 49281 | MinIO Console |
| `VITE_BACKEND_HOST_PORT` | 52891 | ссылки в API docs (браузер) |

**Важно:**

- Внутри Docker-сети порты **не меняются** (`backend:8000`, `qdrant:6333` и т.д.) — в `.env` backend менять не нужно.
- Меняются только порты **на хосте** (маппинг `HOST:CONTAINER`).
- `VITE_BACKEND_HOST_PORT` должен совпадать с `OLSP_BACKEND_HOST_PORT`, иначе страница API docs будет указывать неверный URL backend.
- После смены портов перезапустите frontend-контейнер:

```bash
docker compose --env-file deploy/ports.env -f deploy/docker-compose.yml -f deploy/docker-compose.offline.yml -p openlocalsearchparser up -d --no-build frontend
```

---

## Проверка после запуска

Подставьте свои порты из `deploy/ports.env` (ниже — значения по умолчанию).

### Статус контейнеров

```bash
docker compose --env-file deploy/ports.env -f deploy/docker-compose.yml -f deploy/docker-compose.offline.yml -p openlocalsearchparser ps
```

Все сервисы должны быть в состоянии `running` (кроме кратковременных `starting` при первом запуске).

### HTTP-проверки

| URL | Ожидание |
|-----|----------|
| http://localhost:18473 | Frontend UI |
| http://localhost:52891/docs | Swagger UI |
| http://localhost:52891/health | `{"status":"ok"}` или аналог |
| http://localhost:52891/mcp | MCP endpoint (может требовать MCP-клиент) |
| http://localhost:49281 | MinIO Console (логин `minio` / `minio12345`) |
| http://localhost:36144 | Qdrant dashboard |

### Быстрый тест API

```bash
curl -s http://localhost:52891/health
curl -s -X POST http://localhost:52891/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test","limit":3}'
```

### Логи при проблемах

```bash
docker compose --env-file deploy/ports.env \
  -f deploy/docker-compose.yml \
  -f deploy/docker-compose.offline.yml \
  -p openlocalsearchparser \
  logs -f backend worker llama-ocr llama-embedding
```

---

## Интеграция с Open WebUI

Если Open WebUI запущен **в Docker** на той же машине, используйте `host.docker.internal` и **host-порт backend** из `deploy/ports.env`:

```json
{
  "mcpServers": {
    "open-local-search-parser": {
      "url": "http://host.docker.internal:52891/mcp"
    }
  }
}
```

Для внешнего поиска:

- External Search URL: `http://host.docker.internal:52891/api/openwebui/web-search`
- External Loader URL: `http://host.docker.internal:52891/api/openwebui/web-loader`
- API Key: значение `OPENWEBUI_WEB_SEARCH_API_KEY` из `.env`

Если Open WebUI на хосте (не в Docker), используйте `http://localhost:52891/...`.

---

## Обновление оффлайн-установки

1. На машине с интернетом: обновить код, снова запустить `export-offline-bundle`
2. Перенести **новые** `deploy/offline/images/*.tar.gz` и при необходимости обновлённые compose-файлы
3. На оффлайн-машине:

```powershell
.\deploy\scripts\import-offline-bundle.ps1
.\deploy\scripts\offline-up.ps1
```

Compose пересоздаст контейнеры с новыми образами. Данные в томах (`postgres_data`, `qdrant_data`, `minio_data`) сохраняются.

Для полной переустановки с очисткой данных:

```bash
docker compose --env-file deploy/ports.env \
  -f deploy/docker-compose.yml \
  -f deploy/docker-compose.offline.yml \
  -p openlocalsearchparser \
  down -v
```

**Внимание:** `-v` удалит все тома с документами и индексами.

---

## Устранение неполадок

### `docker compose` пытается скачать образы

Убедитесь, что используете **оба** файла compose и флаг `--no-build`:

```bash
docker compose --env-file deploy/ports.env \
  -f deploy/docker-compose.yml \
  -f deploy/docker-compose.offline.yml \
  -p openlocalsearchparser \
  up -d --no-build
```

Или скрипт `offline-up.ps1` / `offline-up.sh`.

### `Error: image not found`

Образы не загружены. Запустите `import-offline-bundle` и проверьте:

```bash
docker images openlocalsearchparser/backend
```

### Порт уже занят

Измените нужную переменную в `deploy/ports.env` и перезапустите compose.

### Frontend открывается, API docs ведут на неверный порт

Синхронизируйте `VITE_BACKEND_HOST_PORT` с `OLSP_BACKEND_HOST_PORT` и перезапустите frontend.

### llama-ocr / llama-embedding не стартуют

- Проверьте наличие GGUF в `model/`
- Проверьте GPU: `nvidia-smi`
- Проверьте логи: `docker logs <container>`

### `manifest.json` отсутствует

`import-offline-bundle` загрузит все `*.tar.gz` из `deploy/offline/images/` автоматически.

### Нехватка места при экспорте

Удалите старые архивы в `deploy/offline/images/` или укажите другой каталог:

```powershell
.\deploy\scripts\export-offline-bundle.ps1 -OutputDir "D:\bundles\olsp-images"
```

```bash
OUTPUT_DIR=/mnt/bundles/olsp-images ./deploy/scripts/export-offline-bundle.sh
```

---

## Справочник: образы и файлы

### Docker-образы в bundle

| Архив | Образ после загрузки |
|-------|----------------------|
| `backend.tar.gz` | `openlocalsearchparser/backend:offline` |
| `worker.tar.gz` | `openlocalsearchparser/worker:offline` |
| `frontend.tar.gz` | `openlocalsearchparser/frontend:offline` |
| `postgres-16-alpine.tar.gz` | `postgres:16-alpine` |
| `qdrant.tar.gz` | `qdrant/qdrant:latest` |
| `redis-7-alpine.tar.gz` | `redis:7-alpine` |
| `minio.tar.gz` | `minio/minio:latest` |
| `llama-cpp-server-cuda.tar.gz` | `ghcr.io/ggml-org/llama.cpp:server-cuda` |

### Скрипты

| Скрипт | Назначение |
|--------|------------|
| `export-offline-bundle.ps1` / `.sh` | Сборка, pull, сохранение в tar.gz |
| `import-offline-bundle.ps1` / `.sh` | Загрузка образов из tar.gz |
| `offline-up.ps1` / `.sh` | Запуск compose в оффлайн-режиме |

### Параметры скриптов

**export-offline-bundle.ps1:**

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `-ProjectRoot` | корень репозитория | Путь к проекту |
| `-OutputDir` | `deploy/offline/images` | Куда сохранять архивы |
| `-ProjectName` | `openlocalsearchparser` | Имя проекта Docker Compose |

**offline-up.ps1:**

| Параметр | Описание |
|----------|----------|
| `-ImportImages` | Сначала импортировать образы, затем запустить |

**Переменные окружения (bash):**

| Переменная | Описание |
|------------|----------|
| `OUTPUT_DIR` | Каталог для экспорта образов |
| `IMAGES_DIR` | Каталог с tar.gz для импорта |
| `PROJECT_NAME` | Имя проекта compose |

---

## Краткая шпаргалка

```powershell
# === ЭКСПОРТ (машина с интернетом) ===
cp .env.example .env
cp deploy\ports.example.env deploy\ports.env
.\deploy\scripts\export-offline-bundle.ps1

# === ИМПОРТ + ЗАПУСК (оффлайн-машина) ===
cp deploy\ports.example.env deploy\ports.env   # если ports.env ещё нет
.\deploy\scripts\offline-up.ps1 -ImportImages

# === ОСТАНОВКА ===
docker compose --env-file deploy/ports.env -f deploy/docker-compose.yml -f deploy/docker-compose.offline.yml -p openlocalsearchparser down
```

---

*Документ относится к структуре репозитория OpenLocalSearchParser. При изменении compose или скриптов обновите этот файл вместе с кодом.*
