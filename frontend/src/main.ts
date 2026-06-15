import { createPinia } from "pinia";
import { createApp } from "vue";

import "@fontsource-variable/inter";
import "@fontsource/metropolis/300.css";
import "@fontsource/metropolis/400.css";
import "@fontsource/metropolis/600.css";
import "@fontsource/metropolis/700.css";

import App from "./App.vue";
import "./assets/tailwind.css";
import "vue-sonner/style.css";
import { vReveal } from "./directives/reveal";
import router from "./router";
import { useAuthStore } from "./stores/auth";

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();
  app.use(pinia);
  app.provide("weight", "bold");
  app.directive("reveal", vReveal);

  // Hydrate auth from the httpOnly cookie before first render so the router
  // guards see the correct logged_in/role.
  const auth = useAuthStore();
  await auth.hydrate();

  app.use(router);
  app.mount("#app");
}

bootstrap();
