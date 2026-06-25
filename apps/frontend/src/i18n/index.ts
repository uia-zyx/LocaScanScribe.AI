import { createI18n } from 'vue-i18n';

export type Locale = 'en' | 'ru';

const storageKey = 'open-local-search-parser.locale';

export const messages = {
  en: {
    nav: {
      search: 'Search',
      documents: 'Documents',
      upload: 'Upload',
      apiDocs: 'API Docs',
      language: 'Language',
      lightTheme: 'Light',
      darkTheme: 'Dark',
      useLightTheme: 'Switch to light theme',
      useDarkTheme: 'Switch to dark theme',
    },
    search: {
      placeholder: 'Search local documents',
      button: 'Search',
      answerTitle: 'Answer',
      answerFound:
        'For “{query}”, I found {count} matching document(s). The strongest match is “{title}”. Key phrase: {snippet}',
      answerEmpty: 'I did not find a clear answer for “{query}” in the indexed documents.',
    },
    documents: {
      title: 'All Documents',
      uploadNew: 'Upload document',
      empty: 'No documents uploaded yet.',
      openRecognized: 'Open recognized text',
      downloadOriginal: 'Download original',
      downloadRecognized: 'Download recognized Markdown',
      loadFailed: 'Failed to load documents',
      rename: 'Rename',
      delete: 'Delete',
      save: 'Save',
      cancel: 'Cancel',
      confirmDelete: 'Delete “{title}”?',
    },
    upload: {
      title: 'Upload Documents',
      tabs: {
        pdf: 'PDF',
        images: 'Images',
        office: 'Office',
        text: 'Text/Markdown',
      },
      choosePdf: 'Choose PDF',
      chooseImage: 'Choose image',
      chooseOffice: 'Choose office file',
      chooseText: 'Choose text/Markdown',
      scannerOcr: 'Best scanner OCR (via libraries)',
      ocrModel: 'OCR model endpoint',
      upload: 'Upload',
      uploadWithOcr: 'Upload with OCR model',
      uploadWithParser: 'Upload with parser',
      uploadText: 'Upload text',
      chooseFileFirst: 'Choose a file first.',
      uploaded: 'Uploaded {name}; document id {id}',
      duplicate: 'Document {name} already exists; opened existing document id {id}',
      processingQueued:
        'Uploaded {name}; OCR is running in the background. Document id {id}',
      processed: 'OCR completed for {name}; document id {id}',
      processingFailed: 'Document processing or indexing failed for {name}. Check backend logs.',
      processingTimeout:
        'OCR is still running in the background. Open the Documents page to check status.',
      failed: 'Upload failed',
      selectedFile: 'Selected file',
      stages: {
        uploading: 'Uploading file',
        processing: 'Recognizing and indexing document',
        processingBackground: 'Recognizing in the background',
        done: 'Done',
        failed: 'Failed',
      },
    },
    document: {
      recognized: 'Recognized Document',
      page: 'Page',
      downloadOriginal: 'Download original',
      downloadRecognized: 'Download recognized Markdown',
      processing: 'OCR is still processing this document. The page will update automatically.',
      processingFailed: 'Document processing or indexing failed for this document.',
      retryProcessing: 'Retry OCR processing',
      retryFailed: 'Failed to retry OCR processing',
      loadFailed: 'Failed to load document',
    },
    apiDocs: {
      title: 'API Documentation',
      subtitle: 'HTTP endpoints for document ingestion, search, and Open WebUI integration.',
      interactive: {
        title: 'Interactive API Reference',
        description:
          'The backend publishes an OpenAPI schema with interactive API reference pages.',
        swagger: 'Try requests in the classic OpenAPI UI.',
        redoc: 'Read a structured reference with schemas.',
        scalar: 'Use a modern API client-style reference.',
        openapi: 'Download the raw OpenAPI schema.',
      },
      core: {
        title: 'Core API',
        health: 'Check that the backend is running.',
        upload: 'Upload a document and queue OCR/indexing.',
        list: 'List documents with status and processing strategy.',
        markdown: 'Return recognized Markdown for a document.',
        search: 'Search indexed local documents.',
        mcpSearch: 'Search endpoint exposed in OpenAPI and published as an MCP tool.',
        reindex: 'Rebuild Qdrant vectors for recognized Markdown documents.',
      },
      openWebUi: {
        title: 'Open WebUI Web Search',
        description:
          'Use these values in Admin Panel -> Settings -> Web Search when the search engine is set to external.',
        searchEngine: 'Search engine',
        externalSearchUrl: 'External web search URL',
        externalLoaderUrl: 'External web loader URL',
        externalApiKey: 'External web search API key',
        frontendBaseUrl: 'Request host used for document links',
        recommendedTitle: 'Recommended Open WebUI options',
        localFetch:
          'When web loader is enabled for local URLs, set ENABLE_RAG_LOCAL_WEB_FETCH=true in Open WebUI.',
        bypassEmbedding:
          'Enable bypass embedding and retrieval in Open WebUI; this API already searches with local embeddings.',
        bypassWebLoader:
          'Enable bypass web loader if you only need returned snippets. Disable it and use the loader URL for full recognized Markdown.',
        trustProxy:
          'Trust provided proxy parameters only when Open WebUI is behind a trusted reverse proxy.',
      },
      mcp: {
        title: 'MCP Server',
        description:
          'The same backend can be connected to MCP-compatible clients. Published tools use selected FastAPI operations and the existing application logic.',
        transport: 'Transport',
        endpoint: 'MCP endpoint',
        tools: 'Published tools',
        clientConfig: 'Example MCP client configuration',
      },
      examples: {
        title: 'Request Examples',
        uploadCurl: 'Upload and queue OCR with curl',
        searchCurl: 'Search indexed documents with curl',
        mcpSearchCurl: 'Search through MCP tools/call',
        openWebUiSearchCurl: 'Open WebUI external search request',
        openWebUiLoaderCurl: 'Open WebUI external loader request',
        pythonTitle: 'Python httpx example',
        pythonDescription:
          'The same workflow can be automated from scripts, tests, or local tools with a regular HTTP client.',
      },
      contract: {
        title: 'External Contract',
        searchRequest: 'Web search request',
        searchResponse: 'Web search response',
        loaderRequest: 'Web loader request',
        loaderResponse: 'Web loader response',
      },
    },
    errors: {
      searchFailed: 'Search failed',
    },
  },
  ru: {
    nav: {
      search: 'Поиск',
      documents: 'Документы',
      upload: 'Загрузка',
      apiDocs: 'API Docs',
      language: 'Язык',
      lightTheme: 'Светлая',
      darkTheme: 'Тёмная',
      useLightTheme: 'Переключить на светлую тему',
      useDarkTheme: 'Переключить на тёмную тему',
    },
    search: {
      placeholder: 'Поиск по локальным документам',
      button: 'Найти',
      answerTitle: 'Ответ',
      answerFound:
        'По запросу «{query}» найдено документов: {count}. Самое сильное совпадение: «{title}». Ключевая фраза: {snippet}',
      answerEmpty: 'Я не нашёл чёткого ответа по запросу «{query}» в проиндексированных документах.',
    },
    documents: {
      title: 'Все документы',
      uploadNew: 'Загрузить документ',
      empty: 'Документы ещё не загружены.',
      openRecognized: 'Открыть распознанный текст',
      downloadOriginal: 'Скачать оригинал',
      downloadRecognized: 'Скачать распознанный Markdown',
      loadFailed: 'Не удалось загрузить документы',
      rename: 'Переименовать',
      delete: 'Удалить',
      save: 'Сохранить',
      cancel: 'Отмена',
      confirmDelete: 'Удалить «{title}»?',
    },
    upload: {
      title: 'Загрузка документов',
      tabs: {
        pdf: 'PDF',
        images: 'Изображения',
        office: 'Office',
        text: 'Текст/Markdown',
      },
      choosePdf: 'Выбрать PDF',
      chooseImage: 'Выбрать изображение',
      chooseOffice: 'Выбрать офисный файл',
      chooseText: 'Выбрать текст/Markdown',
      scannerOcr: 'Лучший сканер OCR (через библиотеки)',
      ocrModel: 'OCR endpoint модели',
      upload: 'Загрузить',
      uploadWithOcr: 'Загрузить через OCR модель',
      uploadWithParser: 'Загрузить через парсер',
      uploadText: 'Загрузить текст',
      chooseFileFirst: 'Сначала выберите файл.',
      uploaded: 'Загружен {name}; document id {id}',
      duplicate: 'Документ {name} уже существует; открыт существующий document id {id}',
      processingQueued:
        'Файл {name} загружен; OCR выполняется в фоне. Document id {id}',
      processed: 'OCR завершён для {name}; document id {id}',
      processingFailed:
        'Обработка или индексация документа не удалась для {name}. Проверьте логи backend.',
      processingTimeout:
        'OCR всё ещё выполняется в фоне. Откройте страницу документов, чтобы проверить статус.',
      failed: 'Ошибка загрузки',
      selectedFile: 'Выбранный файл',
      stages: {
        uploading: 'Загрузка файла',
        processing: 'Распознавание и индексация документа',
        processingBackground: 'Распознавание в фоне',
        done: 'Готово',
        failed: 'Ошибка',
      },
    },
    document: {
      recognized: 'Распознанный документ',
      page: 'Страница',
      downloadOriginal: 'Скачать оригинал',
      downloadRecognized: 'Скачать распознанный Markdown',
      processing: 'OCR ещё обрабатывает этот документ. Страница обновится автоматически.',
      processingFailed: 'Обработка или индексация этого документа не удалась.',
      retryProcessing: 'Повторить OCR обработку',
      retryFailed: 'Не удалось повторно запустить OCR обработку',
      loadFailed: 'Не удалось загрузить документ',
    },
    apiDocs: {
      title: 'Документация API',
      subtitle: 'HTTP endpoints для загрузки документов, поиска и интеграции с Open WebUI.',
      interactive: {
        title: 'Интерактивная API-документация',
        description:
          'Backend публикует OpenAPI schema и интерактивные страницы API reference.',
        swagger: 'Проверяйте запросы в классическом OpenAPI UI.',
        redoc: 'Читайте структурированную документацию со схемами.',
        scalar: 'Используйте современный API reference в стиле API client.',
        openapi: 'Скачать raw OpenAPI schema.',
      },
      core: {
        title: 'Основное API',
        health: 'Проверить, что backend запущен.',
        upload: 'Загрузить документ и поставить OCR/индексацию в очередь.',
        list: 'Получить список документов со статусом и стратегией обработки.',
        markdown: 'Получить распознанный Markdown документа.',
        search: 'Выполнить поиск по локально проиндексированным документам.',
        mcpSearch: 'Search endpoint, доступный в OpenAPI и опубликованный как MCP tool.',
        reindex: 'Пересобрать Qdrant-векторы для уже распознанных Markdown документов.',
      },
      openWebUi: {
        title: 'Веб-поиск Open WebUI',
        description:
          'Используйте эти значения в Admin Panel -> Settings -> Web Search, когда поисковая система установлена в external.',
        searchEngine: 'Поисковая система',
        externalSearchUrl: 'URL-адрес внешнего веб-поиска',
        externalLoaderUrl: 'URL-адрес внешнего веб-загрузчика',
        externalApiKey: 'Внешний ключ API веб-поиска',
        frontendBaseUrl: 'Host запроса, используемый для ссылок на документы',
        recommendedTitle: 'Рекомендуемые параметры Open WebUI',
        localFetch:
          'Если web loader включён для локальных URL, задайте ENABLE_RAG_LOCAL_WEB_FETCH=true в Open WebUI.',
        bypassEmbedding:
          'Включите обход встраивания и извлечения данных в Open WebUI; это API уже ищет через локальные embeddings.',
        bypassWebLoader:
          'Включите обход веб-загрузчика, если достаточно snippets. Отключите его и используйте loader URL для полного распознанного Markdown.',
        trustProxy:
          'Доверяйте заданным параметрам прокси только если Open WebUI стоит за доверенным reverse proxy.',
      },
      mcp: {
        title: 'MCP Server',
        description:
          'Этот же backend можно подключать к MCP-совместимым клиентам. Опубликованные tools используют выбранные FastAPI операции и существующую логику приложения.',
        transport: 'Transport',
        endpoint: 'MCP endpoint',
        tools: 'Опубликованные tools',
        clientConfig: 'Пример конфигурации MCP client',
      },
      examples: {
        title: 'Примеры запросов',
        uploadCurl: 'Загрузка и постановка OCR в очередь через curl',
        searchCurl: 'Поиск по проиндексированным документам через curl',
        mcpSearchCurl: 'Поиск через MCP tools/call',
        openWebUiSearchCurl: 'Запрос external search для Open WebUI',
        openWebUiLoaderCurl: 'Запрос external loader для Open WebUI',
        pythonTitle: 'Пример на Python httpx',
        pythonDescription:
          'Этот же workflow можно автоматизировать из скриптов, тестов или локальных инструментов через обычный HTTP client.',
      },
      contract: {
        title: 'External contract',
        searchRequest: 'Запрос веб-поиска',
        searchResponse: 'Ответ веб-поиска',
        loaderRequest: 'Запрос веб-загрузчика',
        loaderResponse: 'Ответ веб-загрузчика',
      },
    },
    errors: {
      searchFailed: 'Поиск не выполнен',
    },
  },
};

function getInitialLocale(): Locale {
  const savedLocale = localStorage.getItem(storageKey);
  if (savedLocale === 'en' || savedLocale === 'ru') {
    return savedLocale;
  }

  return navigator.language.toLowerCase().startsWith('ru') ? 'ru' : 'en';
}

export const i18n = createI18n({
  legacy: false,
  locale: getInitialLocale(),
  fallbackLocale: 'en',
  messages,
});

export function setLocale(locale: Locale) {
  i18n.global.locale.value = locale;
  localStorage.setItem(storageKey, locale);
}

