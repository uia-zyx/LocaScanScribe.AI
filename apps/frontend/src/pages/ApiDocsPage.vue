<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const frontendBaseUrl = window.location.origin;
const apiBaseUrl = computed(() => {
  const { hostname, protocol } = window.location;
  return `${protocol}//${hostname}:8000`;
});
const openWebUiApiKey = 'locascan-openwebui-local-key';
</script>

<template>
  <main class="api-docs-page">
    <section class="page-heading">
      <div>
        <h1>{{ t('apiDocs.title') }}</h1>
        <p class="page-subtitle">{{ t('apiDocs.subtitle') }}</p>
      </div>
    </section>

    <section class="docs-grid">
      <article class="docs-card">
        <h2>{{ t('apiDocs.core.title') }}</h2>
        <div class="endpoint-list">
          <div>
            <code>POST /api/documents</code>
            <p>{{ t('apiDocs.core.upload') }}</p>
          </div>
          <div>
            <code>GET /api/documents</code>
            <p>{{ t('apiDocs.core.list') }}</p>
          </div>
          <div>
            <code>GET /api/documents/{id}/markdown</code>
            <p>{{ t('apiDocs.core.markdown') }}</p>
          </div>
          <div>
            <code>POST /api/search</code>
            <p>{{ t('apiDocs.core.search') }}</p>
          </div>
        </div>
      </article>

      <article class="docs-card">
        <h2>{{ t('apiDocs.openWebUi.title') }}</h2>
        <p>{{ t('apiDocs.openWebUi.description') }}</p>

        <div class="settings-list">
          <div>
            <span>{{ t('apiDocs.openWebUi.searchEngine') }}</span>
            <code>external</code>
          </div>
          <div>
            <span>{{ t('apiDocs.openWebUi.externalSearchUrl') }}</span>
            <code>{{ apiBaseUrl }}/api/openwebui/web-search</code>
          </div>
          <div>
            <span>{{ t('apiDocs.openWebUi.externalLoaderUrl') }}</span>
            <code>{{ apiBaseUrl }}/api/openwebui/web-loader</code>
          </div>
          <div>
            <span>{{ t('apiDocs.openWebUi.externalApiKey') }}</span>
            <code>{{ openWebUiApiKey }}</code>
          </div>
          <div>
            <span>{{ t('apiDocs.openWebUi.frontendBaseUrl') }}</span>
            <code>{{ frontendBaseUrl }}</code>
          </div>
        </div>

        <div class="recommendation-box">
          <strong>{{ t('apiDocs.openWebUi.recommendedTitle') }}</strong>
          <ul>
            <li>{{ t('apiDocs.openWebUi.bypassEmbedding') }}</li>
            <li>{{ t('apiDocs.openWebUi.bypassWebLoader') }}</li>
            <li>{{ t('apiDocs.openWebUi.trustProxy') }}</li>
          </ul>
        </div>
      </article>

      <article class="docs-card docs-card-wide">
        <h2>{{ t('apiDocs.contract.title') }}</h2>
        <div class="code-grid">
          <div>
            <h3>{{ t('apiDocs.contract.searchRequest') }}</h3>
            <pre><code>{
  "query": "exam tasks",
  "count": 5
}</code></pre>
          </div>
          <div>
            <h3>{{ t('apiDocs.contract.searchResponse') }}</h3>
            <pre><code>[
  {
    "link": "{{ frontendBaseUrl }}/documents/{id}",
    "title": "Document title",
    "snippet": "Matching Markdown fragment"
  }
]</code></pre>
          </div>
          <div>
            <h3>{{ t('apiDocs.contract.loaderRequest') }}</h3>
            <pre><code>{
  "urls": [
    "{{ frontendBaseUrl }}/documents/{id}"
  ]
}</code></pre>
          </div>
          <div>
            <h3>{{ t('apiDocs.contract.loaderResponse') }}</h3>
            <pre><code>[
  {
    "page_content": "# Recognized Markdown",
    "metadata": {
      "source": "{{ frontendBaseUrl }}/documents/{id}",
      "title": "Document title"
    }
  }
]</code></pre>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>
