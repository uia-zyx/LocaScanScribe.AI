<script setup lang="ts">
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';

import { getOriginalDocumentUrl, listDocuments, type DocumentListItem } from '../services/api';

const { t } = useI18n();
const documents = ref<DocumentListItem[]>([]);
const loading = ref(true);
const error = ref('');

onMounted(async () => {
  try {
    documents.value = await listDocuments();
  } catch (requestError) {
    error.value = requestError instanceof Error ? requestError.message : t('documents.loadFailed');
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <main class="documents-page">
    <div class="page-heading">
      <h1>{{ t('documents.title') }}</h1>
      <RouterLink to="/upload">
        <Button :label="t('documents.uploadNew')" icon="pi pi-plus" />
      </RouterLink>
    </div>

    <section v-if="loading" class="loading-state">
      <ProgressSpinner />
    </section>

    <section v-else-if="error" class="error-state">
      {{ error }}
    </section>

    <section v-else-if="documents.length === 0" class="empty-state">
      {{ t('documents.empty') }}
    </section>

    <section v-else class="documents-list">
      <article v-for="document in documents" :key="document.id" class="document-card">
        <div>
          <RouterLink class="result-title" :to="`/documents/${document.id}`">
            {{ document.title }}
          </RouterLink>
          <div class="document-meta">
            {{ document.original_filename }} · {{ document.mime_type }} · {{ document.status }}
          </div>
        </div>

        <div class="document-card-actions">
          <RouterLink :to="`/documents/${document.id}`">
            <Button :label="t('documents.openRecognized')" text />
          </RouterLink>
          <a :href="getOriginalDocumentUrl(document.id)" download>
            <Button :label="t('documents.downloadOriginal')" icon="pi pi-download" text />
          </a>
        </div>
      </article>
    </section>
  </main>
</template>

