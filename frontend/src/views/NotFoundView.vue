<template>
  <div class="min-h-[80vh] flex flex-col items-center justify-center px-6 py-16 select-none">
    <span class="text-[clamp(7rem,20vw,11rem)] font-light leading-none tracking-tighter text-foreground/10 mb-8">
      {{ code }}
    </span>

    <h1 class="font-display text-2xl font-semibold text-foreground mb-2">{{ title }}</h1>
    <p class="text-sm text-muted-foreground text-center max-w-xs mb-8">{{ message }}</p>

    <Button @click="goHome">
      Back to {{ auth.logged_in ? "dashboard" : "home" }}
    </Button>
  </div>
</template>

<script lang="ts" setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import { Button } from "@/components/ui/button";
import { homePathForRole } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const code = computed(() => (route.query.unauthorized ? "403" : "404"));
const title = computed(() =>
  route.query.unauthorized ? "Access denied" : "Page not found",
);
const message = computed(() =>
  route.query.unauthorized
    ? "You don't have permission to view this page."
    : "This page doesn't exist or may have been moved.",
);

function goHome() {
  if (!auth.logged_in) router.push("/");
  else router.push(homePathForRole(auth.role));
}
</script>
