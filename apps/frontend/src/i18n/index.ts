import { createI18n } from 'vue-i18n';

export type Locale = 'en' | 'ru';

const storageKey = 'locascan.locale';

export const messages = {
  en: {
    nav: {
      search: 'Search',
      documents: 'Documents',
      upload: 'Upload',
      language: 'Language',
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
      loadFailed: 'Failed to load documents',
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
      scannerOcr: 'Top scanner OCR',
      ocrModel: 'OCR model via OpenAI API',
      upload: 'Upload',
      uploadWithOcr: 'Upload with OCR model',
      uploadWithParser: 'Upload with parser',
      uploadText: 'Upload text',
      chooseFileFirst: 'Choose a file first.',
      uploaded: 'Uploaded {name}; document id {id}',
    },
    document: {
      recognized: 'Recognized Document',
      downloadOriginal: 'Download original',
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
      language: 'Язык',
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
      loadFailed: 'Не удалось загрузить документы',
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
      scannerOcr: 'Лучший сканер OCR',
      ocrModel: 'OCR модель через OpenAI API',
      upload: 'Загрузить',
      uploadWithOcr: 'Загрузить через OCR модель',
      uploadWithParser: 'Загрузить через парсер',
      uploadText: 'Загрузить текст',
      chooseFileFirst: 'Сначала выберите файл.',
      uploaded: 'Загружен {name}; document id {id}',
    },
    document: {
      recognized: 'Распознанный документ',
      downloadOriginal: 'Скачать оригинал',
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

