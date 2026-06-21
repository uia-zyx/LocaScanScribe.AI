<script setup lang="ts">
import MarkdownIt from 'markdown-it';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import { computed } from 'vue';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';

import {
  getDocument,
  getDocumentMarkdown,
  getOriginalDocumentUrl,
  type DocumentListItem,
} from '../services/api';

const route = useRoute();
const { t } = useI18n();
const documentId = computed(() => String(route.params.id));
const document = ref<DocumentListItem | null>(null);
const markdown = ref('');
const loading = ref(true);
const originalUrl = computed(() => getOriginalDocumentUrl(documentId.value));
const originalFilename = computed(() => document.value?.original_filename ?? 'document');
const markdownRenderer = new MarkdownIt({
  breaks: true,
  html: false,
  linkify: true,
});
const renderedMarkdown = computed(() => markdownRenderer.render(markdown.value));

onMounted(async () => {
  const [documentMetadata, documentMarkdown] = await Promise.all([
    getDocument(documentId.value),
    getDocumentMarkdown(documentId.value),
  ]);

  document.value = documentMetadata;
  markdown.value = documentMarkdown;
  loading.value = false;
});
</script>

<template>
  <main class="document-page">
    <ProgressSpinner v-if="loading" />
    <section v-else>
      <div class="document-actions">
        <h1>{{ t('document.recognized') }}</h1>
        <a :href="originalUrl" :download="originalFilename">
          <Button
            :aria-label="t('document.downloadOriginal')"
            :title="t('document.downloadOriginal')"
            icon="pi pi-download"
            rounded
          />
        </a>
      </div>

      <article class="markdown-reader" v-html="renderedMarkdown"></article>
    </section>
  </main>
</template>

