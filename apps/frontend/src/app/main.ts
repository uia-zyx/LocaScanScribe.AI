import Aura from '@primevue/themes/aura';
import PrimeVue from 'primevue/config';
import { createPinia } from 'pinia';
import { createApp } from 'vue';

import 'katex/dist/katex.min.css';
import 'primeicons/primeicons.css';
import '../styles/main.css';
import App from './App.vue';
import { i18n } from '../i18n';
import { router } from '../router';

createApp(App)
  .use(createPinia())
  .use(router)
  .use(i18n)
  .use(PrimeVue, {
    theme: {
      preset: Aura,
    },
  })
  .mount('#app');

