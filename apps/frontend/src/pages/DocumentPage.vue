<script setup lang="ts">
import MarkdownIt from 'markdown-it';
import markdownItKatex from 'markdown-it-katex';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import { computed } from 'vue';
import { onMounted, onUnmounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';

import {
  getDocument,
  getDocumentMarkdown,
  getOriginalDocumentUrl,
  getRecognizedDocumentUrl,
  getRecognizedFilename,
  type DocumentListItem,
} from '../services/api';

const route = useRoute();
const { t } = useI18n();
const documentId = computed(() => String(route.params.id));
const document = ref<DocumentListItem | null>(null);
const markdown = ref('');
const loading = ref(true);
const error = ref('');
let pollTimer: number | undefined;
const originalUrl = computed(() => getOriginalDocumentUrl(documentId.value));
const originalFilename = computed(() => document.value?.original_filename ?? 'document');
const recognizedUrl = computed(() => getRecognizedDocumentUrl(documentId.value));
const recognizedFilename = computed(() => getRecognizedFilename(originalFilename.value));
const isIndexed = computed(() => document.value?.status === 'indexed');
const isProcessing = computed(() => document.value?.status === 'processing');
const isFailed = computed(() => document.value?.status === 'failed');
const markdownRenderer = new MarkdownIt({
  breaks: true,
  html: false,
  linkify: true,
}).use(markdownItKatex, {
  throwOnError: false,
  errorColor: '#b91c1c',
});
const renderedMarkdown = computed(() => markdownRenderer.render(markdown.value));

async function loadDocument() {
  try {
    const documentMetadata = await getDocument(documentId.value);
    document.value = documentMetadata;

    if (documentMetadata.status === 'indexed' || documentMetadata.status === 'failed') {
      markdown.value = await getDocumentMarkdown(documentId.value);
      stopPolling();
    }
  } catch (requestError) {
    error.value = requestError instanceof Error ? requestError.message : t('document.loadFailed');
    stopPolling();
  } finally {
    loading.value = false;
  }
}

function startPolling() {
  stopPolling();
  pollTimer = window.setInterval(() => {
    void loadDocument();
  }, 3000);
}

function stopPolling() {
  if (pollTimer !== undefined) {
    window.clearInterval(pollTimer);
    pollTimer = undefined;
  }
}

onMounted(async () => {
  await loadDocument();
  if (document.value?.status === 'processing') {
    startPolling();
  }
});

onUnmounted(stopPolling);
</script>

<template>
  <main class="document-page">
    <ProgressSpinner v-if="loading" />
    <section v-else-if="error" class="error-state">
      {{ error }}
    </section>
    <section v-else>
      <div class="document-actions">
        <h1>{{ t('document.recognized') }}</h1>
        <div class="document-download-actions">
          <a :href="originalUrl" :download="originalFilename">
            <Button
              :aria-label="t('document.downloadOriginal')"
              :title="t('document.downloadOriginal')"
              icon="pi pi-download"
              rounded
            />
          </a>
          <a v-if="isIndexed" :href="recognizedUrl" :download="recognizedFilename">
            <Button
              :aria-label="t('document.downloadRecognized')"
              :title="t('document.downloadRecognized')"
              icon="pi pi-file"
              rounded
            />
          </a>
        </div>
      </div>

      <section v-if="isProcessing" class="loading-state">
        <ProgressSpinner />
        <p>{{ t('document.processing') }}</p>
      </section>

      <section v-else-if="isFailed" class="error-state">
        {{ t('document.processingFailed') }}
      </section>

      <article v-else class="markdown-reader" v-html="renderedMarkdown"></article>
    </section>
  </main>
</template>

