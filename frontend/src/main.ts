import { createPinia } from "pinia";
import { createApp } from "vue";

// IBM Plex Sans — Latin subset only, served from npm.
// Generic */N.css imports pull every subset (Cyrillic, Greek, Vietnamese);
// Latin-only cuts the woff2 payload ~7x on first load. Weight 700 unused.
import "@fontsource/ibm-plex-sans/latin-300.css";
import "@fontsource/ibm-plex-sans/latin-400.css";
import "@fontsource/ibm-plex-sans/latin-500.css";
import "@fontsource/ibm-plex-sans/latin-600.css";
// IBM Plex Serif — only the header wordmark uses it (one weight, latin only).
import "@fontsource/ibm-plex-serif/latin-600.css";

import App from "./App.vue";
import "./assets/tailwind.css";
import "vue-sonner/style.css";
import router from "./router";
import { useAuthStore } from "./stores/auth";

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();
  app.use(pinia);

  // Hydrate auth from the httpOnly cookie before first render so the router
  // guards see the correct logged_in/role.
  const auth = useAuthStore();
  await auth.hydrate();

  app.use(router);
  app.mount("#app");
}

bootstrap();
