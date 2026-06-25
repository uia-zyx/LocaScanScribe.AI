import { computed, ref } from 'vue';

export type UiTheme = 'light' | 'dark';

const storageKey = 'open-local-search-parser.theme';
const selectedTheme = ref<UiTheme>(getInitialTheme());

applyTheme(selectedTheme.value);

export const isDarkTheme = computed(() => selectedTheme.value === 'dark');
export const markdownPreviewTheme = computed(() => (isDarkTheme.value ? 'dark' : 'light'));

export function useTheme() {
  return {
    isDarkTheme,
    selectedTheme,
    markdownPreviewTheme,
    toggleTheme,
  };
}

export function toggleTheme() {
  setTheme(selectedTheme.value === 'dark' ? 'light' : 'dark');
}

export function setTheme(theme: UiTheme) {
  selectedTheme.value = theme;
  localStorage.setItem(storageKey, theme);
  applyTheme(theme);
}

function getInitialTheme(): UiTheme {
  const savedTheme = localStorage.getItem(storageKey);
  if (savedTheme === 'light' || savedTheme === 'dark') {
    return savedTheme;
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme: UiTheme) {
  document.documentElement.dataset.theme = theme;
  document.documentElement.classList.toggle('app-dark', theme === 'dark');
}
