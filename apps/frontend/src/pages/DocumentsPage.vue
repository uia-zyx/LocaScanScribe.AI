<script setup lang="ts">
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';

import {
  deleteDocument,
  getOriginalDocumentUrl,
  listDocuments,
  updateDocumentTitle,
  type DocumentListItem,
} from '../services/api';

const { t } = useI18n();
const documents = ref<DocumentListItem[]>([]);
const loading = ref(true);
const error = ref('');
const editingId = ref<string | null>(null);
const editingTitle = ref('');
const savingId = ref<string | null>(null);
const deletingId = ref<string | null>(null);

async function loadDocuments() {
  try {
    loading.value = true;
    documents.value = await listDocuments();
  } catch (requestError) {
    error.value = requestError instanceof Error ? requestError.message : t('documents.loadFailed');
  } finally {
    loading.value = false;
  }
}

function startEdit(document: DocumentListItem) {
  editingId.value = document.id;
  editingTitle.value = document.title;
}

function cancelEdit() {
  editingId.value = null;
  editingTitle.value = '';
}

async function saveTitle(document: DocumentListItem) {
  const nextTitle = editingTitle.value.trim();
  if (!nextTitle) {
    return;
  }

  try {
    savingId.value = document.id;
    const updatedDocument = await updateDocumentTitle(document.id, nextTitle);
    documents.value = documents.value.map((item) =>
      item.id === updatedDocument.id ? updatedDocument : item,
    );
    cancelEdit();
  } finally {
    savingId.value = null;
  }
}

async function removeDocument(document: DocumentListItem) {
  if (!window.confirm(t('documents.confirmDelete', { title: document.title }))) {
    return;
  }

  try {
    deletingId.value = document.id;
    await deleteDocument(document.id);
    documents.value = documents.value.filter((item) => item.id !== document.id);
  } finally {
    deletingId.value = null;
  }
}

onMounted(loadDocuments);
</script>

<template>
  <main class="documents-page">
    <div class="page-heading">
      <h1>{{ t('documents.title') }}</h1>
      <RouterLink to="/upload">
        <Button :aria-label="t('documents.uploadNew')" :title="t('documents.uploadNew')" icon="pi pi-plus" rounded />
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
        <div class="document-card-main">
          <div v-if="editingId === document.id" class="document-edit-form">
            <input v-model="editingTitle" class="document-title-input" />
            <Button
              :aria-label="t('documents.save')"
              :disabled="!editingTitle.trim()"
              :loading="savingId === document.id"
              icon="pi pi-check"
              rounded
              size="small"
              @click="saveTitle(document)"
            />
            <Button
              :aria-label="t('documents.cancel')"
              :disabled="savingId === document.id"
              icon="pi pi-times"
              rounded
              size="small"
              text
              @click="cancelEdit"
            />
          </div>
          <RouterLink v-else class="result-title" :to="`/documents/${document.id}`">
            {{ document.title }}
          </RouterLink>
          <div class="document-meta">
            {{ document.original_filename }} · {{ document.mime_type }}
            <span class="status-badge">{{ document.status }}</span>
          </div>
        </div>

        <div class="document-card-actions">
          <RouterLink :to="`/documents/${document.id}`">
            <Button
              :aria-label="t('documents.openRecognized')"
              :title="t('documents.openRecognized')"
              icon="pi pi-eye"
              rounded
              text
            />
          </RouterLink>
          <Button
            v-if="editingId !== document.id"
            :aria-label="t('documents.rename')"
            :title="t('documents.rename')"
            icon="pi pi-pencil"
            rounded
            text
            :disabled="deletingId === document.id"
            @click="startEdit(document)"
          />
          <Button
            :aria-label="t('documents.delete')"
            :title="t('documents.delete')"
            icon="pi pi-trash"
            :loading="deletingId === document.id"
            rounded
            severity="danger"
            text
            @click="removeDocument(document)"
          />
          <a :href="getOriginalDocumentUrl(document.id)" :download="document.original_filename">
            <Button
              :aria-label="t('documents.downloadOriginal')"
              :title="t('documents.downloadOriginal')"
              icon="pi pi-download"
              rounded
              text
            />
          </a>
        </div>
      </article>
    </section>
  </main>
</template>

