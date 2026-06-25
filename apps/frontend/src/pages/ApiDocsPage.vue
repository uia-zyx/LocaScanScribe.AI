<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const apiBaseUrl = computed(() => {
  const { hostname, protocol } = window.location;
  return `${protocol}//${hostname}:8000`;
});
const openWebUiApiKeyEnv = 'OPENWEBUI_WEB_SEARCH_API_KEY';
const swaggerUrl = computed(() => `${apiBaseUrl.value}/docs`);
const redocUrl = computed(() => `${apiBaseUrl.value}/redoc`);
const scalarUrl = computed(() => `${apiBaseUrl.value}/api/reference`);
const openApiUrl = computed(() => `${apiBaseUrl.value}/openapi.json`);
const mcpUrl = computed(() => `${apiBaseUrl.value}/mcp`);

const uploadCurlExample = computed(() => `curl -X POST "${apiBaseUrl.value}/api/documents" \\
  -F "strategy=ocr_model" \\
  -F "file=@./example.pdf"`);

const searchCurlExample = computed(() => `curl -X POST "${apiBaseUrl.value}/api/search" \\
  -H "Content-Type: application/json" \\
  -d '{"query":"корни уравнения","limit":5}'`);

const mcpSearchCurlExample = computed(() => `curl -X POST "${apiBaseUrl.value}/mcp" \\
  -H "Accept: application/json, text/event-stream" \\
  -H "Content-Type: application/json" \\
  -H "mcp-session-id: <session-id-from-initialize>" \\
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "mcp_search_documents",
      "arguments": {
        "query": "корни уравнения",
        "limit": 5
      }
    }
  }'`);

const openWebUiSearchExample = computed(() => `curl -X POST "${apiBaseUrl.value}/api/openwebui/web-search" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer \${${openWebUiApiKeyEnv}}" \\
  -d '{"query":"корни уравнения","count":3}'`);

const loaderCurlExample = computed(() => `curl -X POST "${apiBaseUrl.value}/api/openwebui/web-loader" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer \${${openWebUiApiKeyEnv}}" \\
  -d '{"urls":["${apiBaseUrl.value}/documents/{id}"]}'`);

const pythonExample = computed(() => `import httpx

api = "${apiBaseUrl.value}"

with httpx.Client(timeout=120) as client:
    with open("example.pdf", "rb") as file:
        upload = client.post(
            f"{api}/api/documents",
            data={"strategy": "ocr_model"},
            files={"file": ("example.pdf", file, "application/pdf")},
        )
        upload.raise_for_status()
        document_id = upload.json()["document_id"]

    search = client.post(
        f"{api}/api/search",
        json={"query": "корни уравнения", "limit": 5},
    )
    search.raise_for_status()
    print(document_id, search.json())`);

const mcpClientConfigExample = computed(() => `{
  "mcpServers": {
    "open-local-search-parser": {
      "url": "${mcpUrl.value}"
    }
  }
}`);
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
      <article class="docs-card docs-card-wide">
        <h2>{{ t('apiDocs.interactive.title') }}</h2>
        <p>{{ t('apiDocs.interactive.description') }}</p>
        <div class="api-link-grid">
          <a :href="swaggerUrl" target="_blank" rel="noreferrer">
            <strong>Swagger UI</strong>
            <span>{{ t('apiDocs.interactive.swagger') }}</span>
          </a>
          <a :href="redocUrl" target="_blank" rel="noreferrer">
            <strong>ReDoc</strong>
            <span>{{ t('apiDocs.interactive.redoc') }}</span>
          </a>
          <a :href="scalarUrl" target="_blank" rel="noreferrer">
            <strong>Scalar</strong>
            <span>{{ t('apiDocs.interactive.scalar') }}</span>
          </a>
          <a :href="openApiUrl" target="_blank" rel="noreferrer">
            <strong>OpenAPI JSON</strong>
            <span>{{ t('apiDocs.interactive.openapi') }}</span>
          </a>
        </div>
      </article>

      <article class="docs-card">
        <h2>{{ t('apiDocs.core.title') }}</h2>
        <div class="endpoint-list">
          <div>
            <code>GET /api/health</code>
            <p>{{ t('apiDocs.core.health') }}</p>
          </div>
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
          <div>
            <code>POST /api/mcp/search</code>
            <p>{{ t('apiDocs.core.mcpSearch') }}</p>
          </div>
          <div>
            <code>POST /api/documents/reindex-vectors</code>
            <p>{{ t('apiDocs.core.reindex') }}</p>
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
            <code>{{ openWebUiApiKeyEnv }}</code>
          </div>
          <div>
            <span>{{ t('apiDocs.openWebUi.frontendBaseUrl') }}</span>
            <code>{{ apiBaseUrl }}</code>
          </div>
        </div>

        <div class="recommendation-box">
          <strong>{{ t('apiDocs.openWebUi.recommendedTitle') }}</strong>
          <ul>
            <li>{{ t('apiDocs.openWebUi.localFetch') }}</li>
            <li>{{ t('apiDocs.openWebUi.bypassEmbedding') }}</li>
            <li>{{ t('apiDocs.openWebUi.bypassWebLoader') }}</li>
            <li>{{ t('apiDocs.openWebUi.trustProxy') }}</li>
          </ul>
        </div>
      </article>

      <article class="docs-card">
        <h2>{{ t('apiDocs.mcp.title') }}</h2>
        <p>{{ t('apiDocs.mcp.description') }}</p>
        <div class="settings-list">
          <div>
            <span>{{ t('apiDocs.mcp.transport') }}</span>
            <code>Streamable HTTP</code>
          </div>
          <div>
            <span>{{ t('apiDocs.mcp.endpoint') }}</span>
            <code>{{ mcpUrl }}</code>
          </div>
          <div>
            <span>{{ t('apiDocs.mcp.tools') }}</span>
            <code>get_health_status, list_documents, get_document_markdown, mcp_search_documents</code>
          </div>
        </div>
        <div class="recommendation-box">
          <strong>{{ t('apiDocs.mcp.clientConfig') }}</strong>
          <pre><code>{{ mcpClientConfigExample }}</code></pre>
        </div>
      </article>

      <article class="docs-card docs-card-wide">
        <h2>{{ t('apiDocs.examples.title') }}</h2>
        <div class="code-grid">
          <div>
            <h3>{{ t('apiDocs.examples.uploadCurl') }}</h3>
            <pre><code>{{ uploadCurlExample }}</code></pre>
          </div>
          <div>
            <h3>{{ t('apiDocs.examples.searchCurl') }}</h3>
            <pre><code>{{ searchCurlExample }}</code></pre>
          </div>
          <div>
            <h3>{{ t('apiDocs.examples.mcpSearchCurl') }}</h3>
            <pre><code>{{ mcpSearchCurlExample }}</code></pre>
          </div>
          <div>
            <h3>{{ t('apiDocs.examples.openWebUiSearchCurl') }}</h3>
            <pre><code>{{ openWebUiSearchExample }}</code></pre>
          </div>
          <div>
            <h3>{{ t('apiDocs.examples.openWebUiLoaderCurl') }}</h3>
            <pre><code>{{ loaderCurlExample }}</code></pre>
          </div>
        </div>
      </article>

      <article class="docs-card docs-card-wide">
        <h2>{{ t('apiDocs.examples.pythonTitle') }}</h2>
        <p>{{ t('apiDocs.examples.pythonDescription') }}</p>
        <pre><code>{{ pythonExample }}</code></pre>
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
    "link": "{{ apiBaseUrl }}/documents/{id}",
    "title": "Document title",
    "snippet": "Matching Markdown fragment"
  }
]</code></pre>
          </div>
          <div>
            <h3>{{ t('apiDocs.contract.loaderRequest') }}</h3>
            <pre><code>{
  "urls": [
    "{{ apiBaseUrl }}/documents/{id}"
  ]
}</code></pre>
          </div>
          <div>
            <h3>{{ t('apiDocs.contract.loaderResponse') }}</h3>
            <pre><code>[
  {
    "page_content": "# Recognized Markdown",
    "metadata": {
      "source": "{{ apiBaseUrl }}/documents/{id}",
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
