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
          overlayHeader ? 'h-32 topbar-mask-gradient' : 'h-14 bg-surface-inverse border-b border-surface-inverse-foreground/10',
        ]"
      />
      <div class="relative mx-auto w-full max-w-7xl h-14 flex items-center justify-between sm:grid sm:grid-cols-[1fr_auto_1fr] px-6">
        <RouterLink to="/" class="flex items-center gap-2.5">
          <BrandMark class="vt-brand h-6 w-auto" />
          <span class="font-display font-semibold text-lg tracking-tight">hearth</span>
        </RouterLink>

        <!-- Desktop nav links (centered) -->
        <nav v-if="!auth.logged_in" class="hidden sm:flex items-center gap-1">
          <RouterLink
            v-for="link in NAV_LINKS"
            :key="link.to"
            :to="link.to"
            class="text-sm px-3 py-1.5 text-surface-inverse-foreground/70 hover:text-surface-inverse-foreground transition-colors"
          >{{ link.label }}</RouterLink>
        </nav>

        <!-- Desktop auth buttons + mobile hamburger -->
        <div class="flex items-center gap-1 justify-end">
          <template v-if="!auth.logged_in">
            <Button
              variant="ghost"
              class="hidden sm:inline-flex rounded-full h-9 px-5 bg-surface-inverse-foreground/10 text-surface-inverse-foreground hover:bg-surface-inverse-foreground/20 hover:text-surface-inverse-foreground"
              @click="$router.push('/login')"
            >Sign in</Button>
            <Button class="hidden sm:inline-flex rounded-full h-9 px-5" @click="$router.push('/register')">
              Get started
            </Button>
          </template>
          <Button
            v-else
            variant="ghost"
            class="hidden sm:inline-flex rounded-full h-9 px-5 bg-surface-inverse-foreground/10 text-surface-inverse-foreground hover:bg-surface-inverse-foreground/20 hover:text-surface-inverse-foreground"
            @click="$router.push(home)"
          >Go to dashboard</Button>

          <Button
            variant="ghost"
            size="icon"
            class="sm:hidden text-surface-inverse-foreground hover:bg-surface-inverse-foreground/10 hover:text-surface-inverse-foreground"
            aria-label="Menu"
            @click="mobileNavOpen = true"
          >
            <PhEquals class="size-5" weight="bold" />
          </Button>
        </div>

        <ResponsiveSheet :open="mobileNavOpen" title="hearth" @close="mobileNavOpen = false">
          <nav class="flex flex-col">
              <template v-if="!auth.logged_in">
                <button class="text-left text-sm font-medium py-1.5 px-1 text-foreground hover:text-primary press transition-colors" @click="router.push('/login'); mobileNavOpen = false">Sign in</button>
                <button class="text-left text-sm font-medium py-1.5 px-1 text-foreground hover:text-primary press transition-colors" @click="router.push('/register'); mobileNavOpen = false">Get started</button>
              </template>
              <button v-else class="text-left text-sm font-medium py-1.5 px-1 text-foreground hover:text-primary press transition-colors" @click="router.push(home); mobileNavOpen = false">Go to dashboard</button>

              <template v-for="group in NAV_GROUPS" :key="group.label">
                <div class="my-2 text-xs font-medium text-foreground/40 px-1 pt-1">{{ group.label }}</div>
                <button
                  v-for="link in group.links"
                  :key="link.to"
                  class="text-left text-sm py-1.5 px-1 text-foreground/80 hover:text-primary press transition-colors"
                  @click="router.push(link.to); mobileNavOpen = false"
                >{{ link.label }}</button>
              </template>
          </nav>
        </ResponsiveSheet>
      </div>
    </header>
    <main :class="['flex-1', !overlayHeader && 'sm:pt-14']">
      <slot />
    </main>

    <footer v-if="isLanding" class="bg-surface-inverse text-surface-inverse-foreground">
      <div class="mx-auto max-w-7xl px-6 py-12 sm:py-16">
        <div class="flex flex-col sm:flex-row sm:justify-between gap-y-10 gap-x-12">
          <div class="max-w-xs">
            <div class="flex items-center gap-2.5">
              <BrandMark class="h-5 w-auto" />
              <span class="font-display font-semibold text-lg tracking-tight leading-none">hearth</span>
            </div>
            <p class="mt-4 text-sm leading-relaxed text-surface-inverse-foreground/60">
              Verified home-service professionals at your doorstep, with honest pricing and real reviews.
            </p>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-12 gap-y-8">
            <div>
              <h3 class="text-[11px] uppercase tracking-wider text-surface-inverse-foreground/60 font-normal mb-3">
                For customers
              </h3>
              <ul class="space-y-2 text-sm">
                <li><RouterLink to="/register" class="text-surface-inverse-foreground/85 hover:underline">Browse services</RouterLink></li>
                <li><RouterLink to="/help" class="text-surface-inverse-foreground/85 hover:underline">Help center</RouterLink></li>
              </ul>
            </div>
            <div>
              <h3 class="text-[11px] uppercase tracking-wider text-surface-inverse-foreground/60 font-normal mb-3">
                For pros
              </h3>
              <ul class="space-y-2 text-sm">
                <li><RouterLink to="/pros" class="text-surface-inverse-foreground/85 hover:underline">Become a pro</RouterLink></li>
                <li><RouterLink to="/pro-app" class="text-surface-inverse-foreground/85 hover:underline">Pro app</RouterLink></li>
              </ul>
            </div>
            <div>
              <h3 class="text-[11px] uppercase tracking-wider text-surface-inverse-foreground/60 font-normal mb-3">
                Legal
              </h3>
              <ul class="space-y-2 text-sm">
                <li><RouterLink to="/privacy" class="text-surface-inverse-foreground/85 hover:underline">Privacy</RouterLink></li>
                <li><RouterLink to="/terms" class="text-surface-inverse-foreground/85 hover:underline">Terms</RouterLink></li>
              </ul>
            </div>
          </div>
        </div>
        <div
          class="mt-10 sm:mt-12 pt-6 border-t border-surface-inverse-foreground/10 text-xs text-surface-inverse-foreground/60"
        >
          © 2026 hearth
        </div>
      </div>
    </footer>

    <!-- Minimal footer — every other public route (terms, privacy, etc) -->
    <footer v-else class="bg-surface-inverse text-surface-inverse-foreground">
      <div
        class="mx-auto max-w-7xl px-6 py-6 flex flex-wrap items-center justify-between gap-x-6 gap-y-3 text-xs"
      >
        <div class="flex items-center gap-2.5">
          <BrandMark class="h-5 w-auto" />
          <span class="font-display font-semibold text-lg tracking-tight leading-none">hearth</span>
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
import {
  PhEquals,
} from '@phosphor-icons/vue';
import { computed, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import { Button } from "@/components/ui/button";
import ResponsiveSheet from "@/components/ui/ResponsiveSheet.vue";
import { homePathForRole } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const home = computed(() => homePathForRole(auth.role));
const mobileNavOpen = ref(false);

const isLanding = computed(() => route.path === "/");
const overlayHeader = isLanding;

const NAV_LINKS = [
  { label: "Browse services", to: "/register" },
  { label: "For pros", to: "/pros" },
  { label: "Help", to: "/help" },
];

const NAV_GROUPS = [
  { label: "Explore", links: [
    { label: "Browse services", to: "/register" },
    { label: "How it works", to: "/help" },
    { label: "Help center", to: "/help" },
  ]},
  { label: "Professionals", links: [
    { label: "Become a pro", to: "/pros" },
    { label: "Pro app", to: "/pro-app" },
  ]},
  { label: "Legal", links: [
    { label: "Privacy", to: "/privacy" },
    { label: "Terms", to: "/terms" },
  ]},
];
</script>
