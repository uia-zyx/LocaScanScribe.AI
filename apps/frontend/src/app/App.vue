<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink, RouterView } from 'vue-router';

import { setLocale, type Locale } from '../i18n';
import { useTheme } from '../theme';

const { locale, t } = useI18n();
const { isDarkTheme, toggleTheme } = useTheme();
const selectedLocale = computed({
  get: () => locale.value as Locale,
  set: (value: Locale) => setLocale(value),
});
</script>

<template>
  <div class="app-shell">
    <header class="top-nav">
      <RouterLink class="brand" to="/">OpenLocalSearchParser</RouterLink>
      <nav class="main-nav">
        <RouterLink to="/">{{ t('nav.search') }}</RouterLink>
        <RouterLink to="/documents">{{ t('nav.documents') }}</RouterLink>
        <RouterLink to="/upload">{{ t('nav.upload') }}</RouterLink>
        <RouterLink to="/api-docs">{{ t('nav.apiDocs') }}</RouterLink>
        <button
          class="theme-toggle"
          type="button"
          :aria-label="isDarkTheme ? t('nav.useLightTheme') : t('nav.useDarkTheme')"
          :title="isDarkTheme ? t('nav.useLightTheme') : t('nav.useDarkTheme')"
          @click="toggleTheme"
        >
          <i :class="isDarkTheme ? 'pi pi-sun' : 'pi pi-moon'" aria-hidden="true"></i>
          <span>{{ isDarkTheme ? t('nav.lightTheme') : t('nav.darkTheme') }}</span>
        </button>
        <label class="language-select">
          <span>{{ t('nav.language') }}</span>
          <select v-model="selectedLocale" aria-label="Language">
            <option value="en">EN</option>
            <option value="ru">RU</option>
          </select>
        </label>
      </nav>
    </header>

    <RouterView />
  </div>
</template>

