<template>
  <LoadingIndicator />
  <component :is="layoutComponent">
    <router-view />
  </component>
  <DemoBar v-if="DEMO && route.meta.layout === 'auth'" />
  <Toaster position="top-right" rich-colors />
</template>

<script lang="ts" setup>
import { computed, defineComponent, h, onMounted } from "vue";
import { useRoute, useRouter, type RouteRecordRaw } from "vue-router";

import DemoBar from "@/components/DemoBar.vue";
import LoadingIndicator from "@/components/LoadingIndicator.vue";
import { Toaster } from "@/components/ui/sonner";
import { useTheme } from "@/composables/useTheme";
import AuthLayout from "@/layouts/AuthLayout.vue";
import DashboardLayout from "@/layouts/DashboardLayout.vue";
import PublicLayout from "@/layouts/PublicLayout.vue";
import { DEMO } from "@/lib/demo/flag";

useTheme();
const route = useRoute();
const router = useRouter();

// Fallback layout with no chrome. Prevents a flash of landing-page chrome
// on /login or /register before route.meta.layout resolves.
const NoChromeLayout = defineComponent({
  name: "NoChromeLayout",
  setup(_, { slots }) {
    return () => h("div", { class: "min-h-screen bg-background" }, slots.default?.());
  },
});

const layoutComponent = computed(() => {
  switch (route.meta.layout) {
    case "dashboard":
      return DashboardLayout;
    case "auth":
      return AuthLayout;
    case "public":
      return PublicLayout;
    default:
      return NoChromeLayout;
  }
});

// After the initial route mounts, warm-load every other route in the
// background. Subsequent navigation finds the chunk already cached.
onMounted(() => {
  window.setTimeout(() => warmAll(router.options.routes), 600);
});

function warmAll(routes: readonly RouteRecordRaw[]): void {
  for (const r of routes) {
    const comp = r.component as unknown;
    if (typeof comp === "function") {
      try {
        (comp as () => Promise<unknown>)();
      } catch {
        // ignore — best-effort prefetch
      }
    }
    if (r.children) warmAll(r.children);
  }
}
</script>
