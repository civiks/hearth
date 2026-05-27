import { createPinia } from "pinia";
import { createApp } from "vue";

import "@fontsource-variable/inter";

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
