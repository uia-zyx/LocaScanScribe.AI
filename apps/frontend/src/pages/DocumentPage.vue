<script setup lang="ts">
import { MdPreview } from 'md-editor-v3';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import VirtualScroller from 'primevue/virtualscroller';
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
  retryDocumentProcessing,
  type DocumentListItem,
} from '../services/api';
import { useTheme } from '../theme';

const route = useRoute();
const { t } = useI18n();
const { markdownPreviewTheme } = useTheme();
const documentId = computed(() => String(route.params.id));
const document = ref<DocumentListItem | null>(null);
const markdown = ref('');
const loading = ref(true);
const error = ref('');
const retrying = ref(false);
let pollTimer: number | undefined;
const originalUrl = computed(() => getOriginalDocumentUrl(documentId.value));
const originalFilename = computed(() => document.value?.original_filename ?? 'document');
const recognizedUrl = computed(() => getRecognizedDocumentUrl(documentId.value));
const recognizedFilename = computed(() => getRecognizedFilename(originalFilename.value));
const isIndexed = computed(() => document.value?.status === 'indexed');
const isProcessing = computed(() => document.value?.status === 'processing');
const isFailed = computed(() => document.value?.status === 'failed');
const markdownPreviewBlocks = computed(() => createMarkdownPreviewBlocks(markdown.value));

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

async function retryProcessing() {
  try {
    retrying.value = true;
    error.value = '';
    markdown.value = '';
    document.value = await retryDocumentProcessing(documentId.value);
    startPolling();
  } catch (requestError) {
    error.value = requestError instanceof Error ? requestError.message : t('document.retryFailed');
  } finally {
    retrying.value = false;
  }
}

onMounted(async () => {
  await loadDocument();
  if (document.value?.status === 'processing') {
    startPolling();
  }
});

onUnmounted(stopPolling);

interface MarkdownPreviewBlock {
  id: string;
  markdown: string;
}

function createMarkdownPreviewBlocks(source: string): MarkdownPreviewBlock[] {
  const normalized = source.trim();
  if (!normalized) {
    return [];
  }

  const pageSections = normalized.split(/(?=^## Page \d+\b)/m).filter(Boolean);
  const sections = pageSections.length > 1 ? pageSections : [normalized];

  return sections.flatMap((section, sectionIndex) =>
    splitMarkdownSection(section, sectionIndex).map((markdown, chunkIndex) => ({
      id: `${sectionIndex}-${chunkIndex}`,
      markdown,
    })),
  );
}

function splitMarkdownSection(section: string, sectionIndex: number): string[] {
  const targetSize = 2600;
  const headingMatch = section.match(/^(#{1,6}\s.+)$/m);
  const heading = headingMatch?.[1] ?? '';
  const paragraphs = section
    .split(/\n{2,}/)
    .map((part) => part.trim())
    .filter(Boolean);

  const chunks: string[] = [];
  let buffer: string[] = [];
  let bufferSize = 0;

  for (const paragraph of paragraphs) {
    if (buffer.length > 0 && bufferSize + paragraph.length > targetSize) {
      chunks.push(withRepeatedHeading(buffer, heading, chunks.length));
      buffer = [];
      bufferSize = 0;
    }

    buffer.push(paragraph);
    bufferSize += paragraph.length;
  }

  if (buffer.length > 0) {
    chunks.push(withRepeatedHeading(buffer, heading, chunks.length));
  }

  return chunks.length > 0 ? chunks : [`## Section ${sectionIndex + 1}\n\n${section}`];
}

function withRepeatedHeading(parts: string[], heading: string, chunkIndex: number): string {
  if (!heading || chunkIndex === 0 || parts[0] === heading) {
    return parts.join('\n\n');
  }

  return `${heading}\n\n${parts.join('\n\n')}`;
}
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
        <p>{{ t('document.processingFailed') }}</p>
        <Button
          :label="t('document.retryProcessing')"
          :loading="retrying"
          icon="pi pi-refresh"
          @click="retryProcessing"
        />
      </section>

      <VirtualScroller
        v-else
        class="markdown-reader virtual-document-preview"
        :items="markdownPreviewBlocks"
        :item-size="620"
      >
        <template #item="{ item }">
          <MdPreview
            :id="`document-preview-${documentId}-${item.id}`"
            class="virtual-markdown-block"
            :model-value="item.markdown"
            preview-theme="github"
            :theme="markdownPreviewTheme"
          />
        </template>
      </VirtualScroller>
    </section>
  </main>
</template>

