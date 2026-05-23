<template>
  <div class="min-h-screen flex flex-col bg-background">
    <header
      :class="[
        'vt-topbar text-white fixed top-0 left-0 right-0 z-30',
        'transition-colors duration-300 ease-out',
        !overlayHeader || scrolledPast ? 'bg-[#161616]' : '',
      ]"
    >
      <div
        class="mx-auto w-full max-w-7xl h-12 flex items-center justify-between px-6"
      >
        <RouterLink to="/" class="vt-brand flex items-center gap-2">
          <BrandMark class="h-4 w-auto" />
          <span class="font-semibold text-base tracking-tight">hearth</span>
        </RouterLink>
        <nav class="flex items-center gap-1">
          <Button
            v-if="!auth.logged_in"
            variant="ghost"
            size="sm"
            class="text-white hover:bg-white/10 hover:text-white"
            @click="$router.push('/login')"
          >
            Sign in
          </Button>
          <Button
            v-if="!auth.logged_in"
            size="sm"
            @click="$router.push('/register')"
          >
            Get started
          </Button>
          <Button
            v-else
            variant="ghost"
            size="sm"
            class="text-white hover:bg-white/10 hover:text-white"
            @click="$router.push(home)"
          >
            Go to dashboard
          </Button>
        </nav>
      </div>
    </header>
    <main :class="['flex-1', !overlayHeader && 'pt-12']">
      <slot />
    </main>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import { Button } from "@/components/ui/button";
import { homePathForRole } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const route = useRoute();
const home = computed(() => homePathForRole(auth.role));

// On the homepage (/) the hero has its own full-bleed background image, so
// the header floats transparently over it instead of sitting on a solid dark bar.
const overlayHeader = computed(() => route.path === "/");

// On the homepage the header bg fades from transparent to solid #161616 once the
// hero's internal top-down gradient is no longer covering the header area
// (~80px of scroll = hero scrim height 128px − header height 48px).
const HERO_SCRIM_HANDOFF_PX = 80;
const scrolledPast = ref(false);

function onScroll() {
  scrolledPast.value = overlayHeader.value && window.scrollY > HERO_SCRIM_HANDOFF_PX;
}

onMounted(() => {
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
});
onUnmounted(() => {
  window.removeEventListener("scroll", onScroll);
});

watch(() => route.path, () => onScroll());
</script>
