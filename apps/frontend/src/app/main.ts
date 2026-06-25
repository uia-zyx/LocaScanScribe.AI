import Aura from '@primevue/themes/aura';
import { definePreset } from '@primevue/themes';
import PrimeVue from 'primevue/config';
import { createPinia } from 'pinia';
import { createApp } from 'vue';

import 'katex/dist/katex.min.css';
import 'md-editor-v3/lib/preview.css';
import 'primeicons/primeicons.css';
import '../styles/main.css';
import App from './App.vue';
import { i18n } from '../i18n';
import { router } from '../router';

const OpenLocalSearchParserPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#f3f7f9',
      100: '#d9e6ee',
      200: '#b8cfdd',
      300: '#96b7cb',
      400: '#7395AE',
      500: '#557A95',
      600: '#466a82',
      700: '#385768',
      800: '#2d4554',
      900: '#243640',
      950: '#101b22',
    },
  },
});

createApp(App)
  .use(createPinia())
  .use(router)
  .use(i18n)
  .use(PrimeVue, {
    theme: {
      preset: OpenLocalSearchParserPreset,
      options: {
        darkModeSelector: '.app-dark',
      },
    },
  })
  .mount('#app');

