# OpenLocalSearchParser

**Local document search and OCR platform with Markdown-based document representation.**

**Локальная платформа для поиска по документам, OCR-обработки и представления распознанного содержимого в Markdown.**

---

## English

### Overview

OpenLocalSearchParser is an application for local deployment that processes PDFs, images, Office files, plain text, and Markdown documents. It stores the original uploaded file, converts recognized content into Markdown, and provides search results with document links and matching text fragments.

The system is designed for environments where document processing should run on local infrastructure. OCR and embedding services are provided by local `llama.cpp` containers, while the application stack is managed with Docker Compose.

### Capabilities

- PDF processing through page rendering and OCR recognition.
- Image OCR through a local model-compatible endpoint.
- Parser-based processing for Office, text, and Markdown files.
- Markdown preview for recognized documents and search snippets.
- Document operations: list, open, rename, delete, download original file, and download recognized Markdown.
- Search interface with answer summary, document links, and text fragments.
- API documentation page with Open WebUI external web search configuration.
- Internationalized frontend with English and Russian locales.
- Docker Compose deployment with frontend, backend, PostgreSQL, Qdrant, Redis, MinIO, OCR, and embedding services.

### Current Status

The application includes document upload, OCR processing, document listing, Markdown preview, persistent storage, background processing, and search endpoints.

Document metadata and recognized Markdown are stored in PostgreSQL. Original files are stored in MinIO. Markdown chunks are embedded through the local embedding service and indexed in Qdrant for vector search.

### Architecture

```text
apps/
  backend/      FastAPI API, ingestion, parsing, OCR orchestration
  frontend/     Vue 3 + Pinia + PrimeVue client
deploy/
  docker-compose.yml
model/
  local GGUF model files, ignored by git
```

Runtime services:

- `frontend`: Vue 3 application served on `http://localhost:18473`
- `backend`: FastAPI API served on `http://localhost:52891`
- `llama-ocr`: OCR model server
- `llama-embedding`: embedding model server
- `postgres`: document metadata and recognized Markdown persistence
- `qdrant`: vector index for Markdown chunks
- `redis`: background processing queue
- `minio`: original document object storage

### Models

Model binaries are ignored by Git. Place them in `model/`:

- `GLM-OCR-Q8_0.gguf`
- `mmproj-GLM-OCR-Q8_0.gguf`
- `Qwen3-Embedding-0.6B-Q8_0.gguf`

The embedding service runs with:

```text
--embedding --pooling last
```

### Installation

Requirements:

- Docker Desktop
- NVIDIA GPU and NVIDIA Container Toolkit for GPU inference
- Local GGUF files in `model/`

Run:

```bash
cp .env.example .env
cp deploy/ports.example.env deploy/ports.env
docker compose --env-file deploy/ports.env -f deploy/docker-compose.yml up -d --build
```

Host ports are configured in `deploy/ports.env`. Change values there if any port is already in use on your machine. Keep `VITE_BACKEND_HOST_PORT` in sync with `OLSP_BACKEND_HOST_PORT` so API docs links stay correct.

Open (default ports from `deploy/ports.example.env`):

- Frontend: `http://localhost:18473`
- Backend OpenAPI: `http://localhost:52891/docs`
- API Documentation: `http://localhost:18473/api-docs`
- MCP Server: `http://localhost:52891/mcp`
- MinIO Console: `http://localhost:49281`
- Qdrant: `http://localhost:36144`

### Offline Docker Deployment

See the full guide: **[deploy/OFFLINE-DEPLOYMENT.md](deploy/OFFLINE-DEPLOYMENT.md)** (RU).

Quick start:

```powershell
# Windows
.\deploy\scripts\export-offline-bundle.ps1
```

```bash
# Linux/macOS
chmod +x deploy/scripts/*.sh
./deploy/scripts/export-offline-bundle.sh
```

This builds local images, pulls third-party images, and saves everything to `deploy/offline/images/*.tar.gz` plus `manifest.json`.

**Copy to the offline machine:**

- `deploy/offline/images/`
- `deploy/ports.env` (or `deploy/ports.example.env`)
- `deploy/docker-compose.yml`
- `deploy/docker-compose.offline.yml`
- `deploy/scripts/`
- `.env` and `model/` with GGUF files

**On the offline machine (import and start):**

```powershell
.\deploy\scripts\import-offline-bundle.ps1
.\deploy\scripts\offline-up.ps1
```

```bash
./deploy/scripts/import-offline-bundle.sh
./deploy/scripts/offline-up.sh
```

Or import and start in one step:

```powershell
.\deploy\scripts\offline-up.ps1 -ImportImages
```

```bash
./deploy/scripts/offline-up.sh --import
```

Offline mode uses pre-loaded images from `deploy/docker-compose.offline.yml` and does not rebuild containers.

### PDF OCR Flow

```text
PDF upload
  -> render each page to an image
  -> send each page image to llama.cpp OCR
  -> collect page Markdown
  -> show recognized Markdown in the browser
```

Images go directly to OCR. Office and text formats go through the parser path.

### Open WebUI Integration

Set Web Search Engine to `external` and use the same host that serves the backend:

- External Search URL: `http://<backend-host>:52891/api/openwebui/web-search`
- External Loader URL: `http://<backend-host>:52891/api/openwebui/web-loader`
- External Search API Key: value of `OPENWEBUI_WEB_SEARCH_API_KEY`

Returned document links use the incoming request host or `Origin` header. For snippet-based results, enable bypass embedding and retrieval and bypass web loader in Open WebUI. For full recognized Markdown, configure the external loader URL and keep web loader bypass disabled.

### MCP Server

The backend exposes selected FastAPI operations through MCP over Streamable HTTP:

```json
{
  "mcpServers": {
    "open-local-search-parser": {
      "url": "http://localhost:52891/mcp"
    }
  }
}
```

For clients running inside Docker containers, use `http://host.docker.internal:52891/mcp` instead of `localhost`.

Published operations cover health checks, document listing, document metadata, recognized Markdown, vector reindexing, and document search. Binary downloads remain available through the regular HTTP API.

Search is available through both interfaces:

- OpenAPI/HTTP: `POST /api/search`
- MCP/OpenAPI bridge: `POST /api/mcp/search`
- MCP URL with OpenAPI discovery: `GET /mcp/openapi.json`, `POST /mcp/search`
- MCP tool name: `mcp_search_documents`

---

## Русский

### Обзор

OpenLocalSearchParser — приложение для локального развертывания, предназначенное для обработки PDF, изображений, Office-файлов, обычного текста и Markdown-документов. Система сохраняет исходный файл, преобразует распознанное содержимое в Markdown и предоставляет поиск по документам с ссылками и фрагментами совпадений.

Система рассчитана на сценарии, где обработка документов должна выполняться на локальной инфраструктуре. OCR и embeddings обслуживаются локальными контейнерами `llama.cpp`, а весь стек запускается через Docker Compose.

### Возможности

- Обработка PDF через рендеринг страниц и OCR-распознавание.
- OCR изображений через локальный model-compatible endpoint.
- Parser-based обработка Office-файлов, текста и Markdown.
- Markdown preview для распознанных документов и фрагментов поиска.
- Операции с документами: список, открытие, переименование, удаление, скачивание оригинала и распознанного Markdown.
- Поисковый интерфейс с кратким ответом, ссылками на документы и фрагментами совпадений.
- Страница документации API с настройками внешнего web-search для Open WebUI.
- Интерфейс на русском и английском языках.
- Docker Compose стек с frontend, backend, PostgreSQL, Qdrant, Redis, MinIO, OCR и embedding сервисами.

### Текущий Статус

Приложение включает загрузку документов, OCR-обработку, список документов, Markdown preview, постоянное хранение, фоновые задачи и поисковые API.

Metadata документов и распознанный Markdown сохраняются в PostgreSQL. Оригинальные файлы хранятся в MinIO. Markdown chunks проходят embedding через локальный embedding service и индексируются в Qdrant для vector search.

### Архитектура

```text
apps/
  backend/      FastAPI API, ingestion, parsing, OCR orchestration
  frontend/     Vue 3 + Pinia + PrimeVue client
deploy/
  docker-compose.yml
model/
  локальные GGUF модели, не попадают в Git
```

Сервисы:

- `frontend`: Vue 3 приложение на `http://localhost:18473`
- `backend`: FastAPI API на `http://localhost:52891`
- `llama-ocr`: OCR model server
- `llama-embedding`: embedding model server
- `postgres`: хранение metadata документов и распознанного Markdown
- `qdrant`: vector index для Markdown chunks
- `redis`: очередь фоновой обработки
- `minio`: object storage для оригинальных файлов

### Модели

Файлы моделей игнорируются Git. Положите их в `model/`:

- `GLM-OCR-Q8_0.gguf`
- `mmproj-GLM-OCR-Q8_0.gguf`
- `Qwen3-Embedding-0.6B-Q8_0.gguf`

Embedding service запускается с:

```text
--embedding --pooling last
```

### Установка

Требования:

- Docker Desktop
- NVIDIA GPU и NVIDIA Container Toolkit для GPU inference
- GGUF модели в `model/`

Запуск:

```bash
cp .env.example .env
cp deploy/ports.example.env deploy/ports.env
docker compose --env-file deploy/ports.env -f deploy/docker-compose.yml up -d --build
```

Порты на хосте задаются в `deploy/ports.env`. Меняйте их, если порт уже занят. Держите `VITE_BACKEND_HOST_PORT` равным `OLSP_BACKEND_HOST_PORT`, чтобы ссылки в API docs оставались корректными.

Открыть (порты по умолчанию из `deploy/ports.example.env`):

- Frontend: `http://localhost:18473`
- Backend OpenAPI: `http://localhost:52891/docs`
- API Documentation: `http://localhost:18473/api-docs`
- MCP Server: `http://localhost:52891/mcp`
- MinIO Console: `http://localhost:49281`
- Qdrant: `http://localhost:36144`

### Оффлайн развёртывание Docker

Полное руководство: **[deploy/OFFLINE-DEPLOYMENT.md](deploy/OFFLINE-DEPLOYMENT.md)**.

Кратко:

```powershell
.\deploy\scripts\export-offline-bundle.ps1
```

```bash
chmod +x deploy/scripts/*.sh
./deploy/scripts/export-offline-bundle.sh
```

Скрипт собирает локальные образы, скачивает сторонние и сохраняет всё в `deploy/offline/images/*.tar.gz` и `manifest.json`.

**Скопируйте на оффлайн-машину:**

- `deploy/offline/images/`
- `deploy/ports.env` (или `deploy/ports.example.env`)
- `deploy/docker-compose.yml`
- `deploy/docker-compose.offline.yml`
- `deploy/scripts/`
- `.env` и `model/` с GGUF-файлами

**На оффлайн-машине (импорт и запуск):**

```powershell
.\deploy\scripts\import-offline-bundle.ps1
.\deploy\scripts\offline-up.ps1
```

```bash
./deploy/scripts/import-offline-bundle.sh
./deploy/scripts/offline-up.sh
```

Или импорт и запуск одной командой:

```powershell
.\deploy\scripts\offline-up.ps1 -ImportImages
```

```bash
./deploy/scripts/offline-up.sh --import
```

В оффлайн-режиме используются предзагруженные образы из `deploy/docker-compose.offline.yml`, без пересборки контейнеров.

### PDF OCR Flow

```text
Загрузка PDF
  -> каждая страница рендерится в изображение
  -> изображение каждой страницы отправляется в llama.cpp OCR
  -> результаты собираются в Markdown по страницам
  -> распознанный Markdown отображается в браузере
```

Изображения сразу идут в OCR. Office и текстовые форматы идут через parser path.

### Интеграция Open WebUI

Установите Web Search Engine в `external` и используйте тот же host, на котором доступен backend:

- External Search URL: `http://<backend-host>:52891/api/openwebui/web-search`
- External Loader URL: `http://<backend-host>:52891/api/openwebui/web-loader`
- External Search API Key: значение `OPENWEBUI_WEB_SEARCH_API_KEY`

Ссылки на документы используют host входящего запроса или `Origin` header. Для быстрых результатов по snippets включите bypass embedding and retrieval и bypass web loader в Open WebUI. Для полного распознанного Markdown настройте external loader URL и отключите bypass web loader.

### MCP Server

Backend публикует выбранные FastAPI операции через MCP по Streamable HTTP:

```json
{
  "mcpServers": {
    "open-local-search-parser": {
      "url": "http://localhost:52891/mcp"
    }
  }
}
```

Для клиентов, запущенных внутри Docker-контейнеров, используйте `http://host.docker.internal:52891/mcp` вместо `localhost`.

Опубликованные операции покрывают health check, список документов, metadata документа, распознанный Markdown, переиндексацию vector store и поиск по документам. Скачивание бинарных файлов остаётся в обычном HTTP API.

Поиск доступен через оба интерфейса:

- OpenAPI/HTTP: `POST /api/search`
- MCP/OpenAPI bridge: `POST /api/mcp/search`
- MCP URL с OpenAPI discovery: `GET /mcp/openapi.json`, `POST /mcp/search`
- MCP tool name: `mcp_search_documents`

