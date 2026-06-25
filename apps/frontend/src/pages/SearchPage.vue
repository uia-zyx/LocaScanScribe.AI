<script setup lang="ts">
import { MdPreview } from 'md-editor-v3';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import ProgressSpinner from 'primevue/progressspinner';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink, useRoute, useRouter } from 'vue-router';

import { localizeMarkdownPageHeadings } from '../markdown/localization';
import { useSearchStore } from '../stores/searchStore';
import { useTheme } from '../theme';

const route = useRoute();
const router = useRouter();
const store = useSearchStore();
const { t } = useI18n();
const { markdownPreviewTheme } = useTheme();
const query = ref(String(route.query.q ?? ''));
const answer = computed(() => {
  if (!store.query) {
    return '';
  }

  if (store.results.length === 0) {
    return t('search.answerEmpty', { query: store.query });
  }

  const topResult = store.results[0];
  const topSnippet = topResult.snippets[0]?.phrase ?? '';
  return t('search.answerFound', {
    query: store.query,
    count: store.results.length,
    title: topResult.title,
    snippet: localizeSearchMarkdown(topSnippet),
  });
});

function localizeSearchMarkdown(markdown: string): string {
  return localizeMarkdownPageHeadings(markdown, t('document.page'));
}

async function submitSearch() {
  if (!query.value.trim()) {
    return;
  }

  await router.replace({ path: '/', query: { q: query.value } });
  await store.search(query.value);
}

if (query.value) {
  void store.search(query.value);
}
</script>

<template>
  <main class="search-page">
    <section class="hero-search">
      <h1>OpenLocalSearchParser</h1>
      <form class="search-box" @submit.prevent="submitSearch">
        <InputText v-model="query" class="search-input" :placeholder="t('search.placeholder')" />
        <Button :label="t('search.button')" type="submit" />
      </form>
    </section>

    <section v-if="store.loading" class="loading-state">
      <ProgressSpinner />
    </section>

    <section v-else-if="store.error" class="error-state">
      {{ store.error }}
    </section>

    <section v-else class="results">
      <article v-if="answer" class="answer-card">
        <h2>{{ t('search.answerTitle') }}</h2>
        <MdPreview
          id="search-answer-preview"
          class="search-markdown-preview"
          :model-value="answer"
          preview-theme="github"
          :theme="markdownPreviewTheme"
        />
      </article>

      <article v-for="item in store.results" :key="item.document_id" class="result-card">
        <RouterLink class="result-title" :to="item.url">{{ item.title }}</RouterLink>
        <div class="result-url">{{ item.url }}</div>
        <MdPreview
          v-for="snippet in item.snippets"
          :id="`snippet-preview-${snippet.chunk_id}`"
          :key="snippet.chunk_id"
          class="snippet search-markdown-preview"
          :model-value="localizeSearchMarkdown(snippet.phrase)"
          preview-theme="github"
          :theme="markdownPreviewTheme"
        />
      </article>
    </section>
  </main>
</template>

