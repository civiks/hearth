<template>
  <div class="min-h-dvh flex flex-col bg-background">
    <header
      :class="[
        'vt-topbar text-surface-inverse-foreground top-0 left-0 right-0 z-30',
        isLanding ? 'fixed' : 'relative sm:fixed',
      ]"
    >

      <div
        aria-hidden="true"
        :class="[
          'pointer-events-none absolute inset-x-0 top-0',
          overlayHeader ? 'h-32 topbar-mask-gradient' : 'h-12 bg-surface-inverse',
        ]"
      />
      <div
        class="relative mx-auto w-full max-w-7xl h-12 flex items-center justify-between px-6"
      >
        <RouterLink to="/" class="vt-brand flex items-center gap-2">
          <BrandMark class="h-4 w-auto" />
          <span class="brand-wordmark font-semibold text-base tracking-tight">hearth</span>
        </RouterLink>
        <nav class="flex items-center gap-1">
          <Button
            v-if="!auth.logged_in"
            variant="ghost"
            size="sm"
            class="text-surface-inverse-foreground hover:bg-surface-inverse-foreground/10 hover:text-surface-inverse-foreground"
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
            class="text-surface-inverse-foreground hover:bg-surface-inverse-foreground/10 hover:text-surface-inverse-foreground"
            @click="$router.push(home)"
          >
            Go to dashboard
          </Button>
        </nav>
      </div>
    </header>
    <main :class="['flex-1', !overlayHeader && 'sm:pt-12']">
      <slot />
    </main>

    <footer v-if="isLanding" class="bg-surface-inverse text-surface-inverse-foreground">
      <div class="mx-auto max-w-7xl px-6 py-10">
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-8">
          <div class="col-span-2 sm:col-span-1">
            <div class="flex items-center gap-2">
              <BrandMark class="h-5 w-auto" />
              <span class="brand-wordmark font-semibold text-base tracking-tight leading-none">hearth</span>
            </div>
          </div>
          <div>
            <h3
              class="text-[11px] uppercase tracking-wider text-surface-inverse-foreground/60 font-normal mb-3"
            >
              For customers
            </h3>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="text-surface-inverse-foreground/85 hover:underline">Book a service</a></li>
              <li><a href="#" class="text-surface-inverse-foreground/85 hover:underline">Browse services</a></li>
              <li><a href="#" class="text-surface-inverse-foreground/85 hover:underline">Help center</a></li>
            </ul>
          </div>
          <div>
            <h3
              class="text-[11px] uppercase tracking-wider text-surface-inverse-foreground/60 font-normal mb-3"
            >
              For pros
            </h3>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="text-surface-inverse-foreground/85 hover:underline">Become a pro</a></li>
              <li><a href="#" class="text-surface-inverse-foreground/85 hover:underline">Pro resources</a></li>
              <li><a href="#" class="text-surface-inverse-foreground/85 hover:underline">Pro app</a></li>
            </ul>
          </div>
        </div>
        <div
          class="mt-8 pt-6 border-t border-surface-inverse-foreground/10 flex flex-wrap items-center justify-between gap-x-6 gap-y-2 text-xs text-surface-inverse-foreground/60"
        >
          <span>© 2026 hearth</span>
          <div class="flex gap-x-6">
            <RouterLink to="/privacy" class="hover:underline">Privacy</RouterLink>
            <RouterLink to="/terms" class="hover:underline">Terms</RouterLink>
          </div>
        </div>
      </div>
    </footer>

    <!-- Minimal footer — every other public route (terms, privacy, etc) -->
    <footer v-else class="bg-surface-inverse text-surface-inverse-foreground">
      <div
        class="mx-auto max-w-7xl px-6 py-6 flex flex-wrap items-center justify-between gap-x-6 gap-y-3 text-xs"
      >
        <div class="flex items-center gap-2">
          <BrandMark class="h-4 w-auto" />
          <span class="brand-wordmark font-semibold tracking-tight leading-none">hearth</span>
          <span class="text-surface-inverse-foreground/60 ml-3">© 2026</span>
        </div>
        <div class="flex flex-wrap items-center gap-x-6 gap-y-2 text-surface-inverse-foreground/70">
          <RouterLink to="/privacy" class="hover:underline">Privacy</RouterLink>
          <RouterLink to="/terms" class="hover:underline">Terms</RouterLink>
        </div>
      </div>
    </footer>
  </div>
</template>

<script lang="ts" setup>
import { computed } from "vue";
import { RouterLink, useRoute } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import { Button } from "@/components/ui/button";
import { homePathForRole } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const route = useRoute();
const home = computed(() => homePathForRole(auth.role));

// On the homepage (/) the hero has its own full-bleed background image, so
// the header floats over it with a soft mask-gradient backdrop instead of
// sitting on a solid dark bar. Landing also gets the full footer (link
// columns); /terms, /privacy, etc. get the minimal one-row variant.
const isLanding = computed(() => route.path === "/");
const overlayHeader = isLanding;
</script>
