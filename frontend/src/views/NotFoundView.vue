<template>
  <div class="min-h-[60vh] flex items-center justify-center px-6 py-16">
    <div class="text-center max-w-md">
      <h1 class="text-7xl font-light text-foreground mb-2">{{ code }}</h1>
      <h2 class="text-xl font-light mb-3">{{ title }}</h2>
      <p class="text-sm text-muted-foreground mb-6">{{ message }}</p>
      <Button @click="goHome">
        <Home class="mr-2 size-4" />
        Back to {{ auth.logged_in ? "dashboard" : "home" }}
      </Button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Home } from "lucide-vue-next";
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
    ? "You do not have permission to access this page."
    : "The page you are looking for does not exist.",
);

function goHome() {
  if (!auth.logged_in) router.push("/");
  else router.push(homePathForRole(auth.role));
}
</script>
