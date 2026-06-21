import { createI18n } from 'vue-i18n';

export type Locale = 'en' | 'ru';

const storageKey = 'locascan.locale';

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
      ocrModel: 'OCR model via OpenAI API (via model)',
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
      processingFailed: 'OCR processing failed for {name}. Check backend logs.',
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
      downloadOriginal: 'Download original',
      downloadRecognized: 'Download recognized Markdown',
      processing: 'OCR is still processing this document. The page will update automatically.',
      processingFailed: 'OCR processing failed for this document.',
      retryProcessing: 'Retry OCR processing',
      retryFailed: 'Failed to retry OCR processing',
      loadFailed: 'Failed to load document',
    },
    apiDocs: {
      title: 'API Documentation',
      subtitle: 'HTTP endpoints for document ingestion, search, and Open WebUI integration.',
      core: {
        title: 'Core API',
        upload: 'Upload a document and queue OCR/indexing.',
        list: 'List documents with status and processing strategy.',
        markdown: 'Return recognized Markdown for a document.',
        search: 'Search indexed local documents.',
      },
      openWebUi: {
        title: 'Open WebUI Web Search',
        description:
          'Use these values in Admin Panel -> Settings -> Web Search when the search engine is set to external.',
        searchEngine: 'Search engine',
        externalSearchUrl: 'External web search URL',
        externalLoaderUrl: 'External web loader URL',
        externalApiKey: 'External web search API key',
        frontendBaseUrl: 'Document link base URL',
        recommendedTitle: 'Recommended Open WebUI options',
        bypassEmbedding: 'Enable bypass embedding and retrieval for quick snippet-based results.',
        bypassWebLoader:
          'Enable bypass web loader if you only need returned snippets. Disable it and use the loader URL for full recognized Markdown.',
        trustProxy:
          'Trust provided proxy parameters only when Open WebUI is behind a trusted reverse proxy.',
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
      ocrModel: 'OCR модель через OpenAI API (через модель)',
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
      processingFailed: 'OCR обработка не удалась для {name}. Проверьте логи backend.',
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
      downloadOriginal: 'Скачать оригинал',
      downloadRecognized: 'Скачать распознанный Markdown',
      processing: 'OCR ещё обрабатывает этот документ. Страница обновится автоматически.',
      processingFailed: 'OCR обработка этого документа не удалась.',
      retryProcessing: 'Повторить OCR обработку',
      retryFailed: 'Не удалось повторно запустить OCR обработку',
      loadFailed: 'Не удалось загрузить документ',
    },
    apiDocs: {
      title: 'Документация API',
      subtitle: 'HTTP endpoints для загрузки документов, поиска и интеграции с Open WebUI.',
      core: {
        title: 'Основное API',
        upload: 'Загрузить документ и поставить OCR/индексацию в очередь.',
        list: 'Получить список документов со статусом и стратегией обработки.',
        markdown: 'Получить распознанный Markdown документа.',
        search: 'Выполнить поиск по локально проиндексированным документам.',
      },
      openWebUi: {
        title: 'Веб-поиск Open WebUI',
        description:
          'Используйте эти значения в Admin Panel -> Settings -> Web Search, когда поисковая система установлена в external.',
        searchEngine: 'Поисковая система',
        externalSearchUrl: 'URL-адрес внешнего веб-поиска',
        externalLoaderUrl: 'URL-адрес внешнего веб-загрузчика',
        externalApiKey: 'Внешний ключ API веб-поиска',
        frontendBaseUrl: 'Базовый URL ссылок на документы',
        recommendedTitle: 'Рекомендуемые параметры Open WebUI',
        bypassEmbedding:
          'Включите обход встраивания и извлечения данных для быстрых результатов по snippets.',
        bypassWebLoader:
          'Включите обход веб-загрузчика, если достаточно snippets. Отключите его и используйте loader URL для полного распознанного Markdown.',
        trustProxy:
          'Доверяйте заданным параметрам прокси только если Open WebUI стоит за доверенным reverse proxy.',
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

