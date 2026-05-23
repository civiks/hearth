<template>
  <Transition
    enter-active-class="transition-opacity duration-200 ease-out"
    enter-from-class="opacity-0"
    leave-active-class="transition-opacity duration-150 ease-out"
    leave-to-class="opacity-0"
  >
    <div
      v-if="visible"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-background/60 backdrop-blur-sm pointer-events-none"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="80"
        height="60"
        fill="none"
        viewBox="0 0 80 60"
        class="h-12 w-auto text-muted-foreground/40 animate-pulse"
        aria-hidden="true"
      >
        <path
          fill="currentColor"
          d="M0 28.5h3.019v3H0zM10.566 15h6.038v6h-6.038zm0 24h6.038v6h-6.038zM20.629 1h10.063v10H20.629zm-2.013 48h10.063v10H20.629zm14.088-36h10.063v10H32.704zm0 24h10.063v10H32.704zm11.07-37h12.075v12H43.774zm1.006 25h10.063v10H44.78zm-1.006 23h12.075v12H43.774zM55.85 12h12.074v12H55.85zm0 24h12.074v12H55.85zm12.075-10H80v12H67.924z"
        />
      </svg>
    </div>
  </Transition>
  <div role="status" aria-live="polite" class="sr-only">
    {{ announcement }}
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { useRouter, type RouteLocationNormalized } from "vue-router";

const router = useRouter();
const visible = ref(false);
const announcement = ref("");
let showTimer: number | undefined;

// 150ms grace before showing the loader — skips flicker on chunks that are
// already in memory (post-warmup). For cold first loads on GH Pages this
// fires almost immediately.
const SHOW_DELAY_MS = 150;

router.beforeEach((to) => {
  if (showTimer) window.clearTimeout(showTimer);
  showTimer = window.setTimeout(() => {
    visible.value = true;
  }, SHOW_DELAY_MS);
  announcement.value = `Loading ${prettyName(to)}…`;
});

router.afterEach((to) => {
  if (showTimer) {
    window.clearTimeout(showTimer);
    showTimer = undefined;
  }
  visible.value = false;
  announcement.value = `${prettyName(to)} loaded`;
});

function prettyName(r: RouteLocationNormalized): string {
  const path = r.path || "/";
  if (path === "/") return "home";
  return path.replace(/^\//, "").replace(/\//g, " ");
}
</script>
