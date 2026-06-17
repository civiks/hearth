<template>
  <div>
    <!-- Hero — full-bleed image with a left-side dark gradient scrim under the CTA copy -->
    <section
      data-public-hero
      class="relative bg-surface-inverse text-surface-inverse-foreground overflow-hidden"
    >
      <div class="relative mx-auto max-w-7xl">
        <div class="relative px-6 pt-24 pb-16 sm:pt-28 sm:pb-20">
          <div class="max-w-xl">
            <div v-reveal class="inline-flex items-center gap-1.5 mb-4 sm:mb-5 text-sm font-medium tracking-tight text-surface-inverse-foreground/55">
              <PhMapPin class="size-3.5 text-surface-inverse-foreground/70" weight="bold" />
              Now in Bangalore
            </div>
            <h1 v-reveal="80" class="font-display text-4xl sm:text-5xl font-semibold tracking-[-0.03em] mb-5 sm:mb-6 leading-[1.05] text-balance text-transparent bg-clip-text bg-gradient-to-b from-white via-zinc-100 to-zinc-400">
              Home services, done right.
            </h1>
            <p v-reveal="160" class="text-base sm:text-lg text-surface-inverse-foreground/65 mb-7 sm:mb-8 max-w-lg leading-relaxed tracking-[-0.01em]">
              Verified plumbers, electricians, cleaners and more. At your doorstep within hours, with honest pricing and real reviews.
            </p>
          </div>
          <div v-reveal="240" class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-x-12 gap-y-7">
            <div>
            <div class="flex flex-wrap gap-3">
              <template v-if="DEMO">
                <DropdownMenu v-if="isDesktop" :modal="false">
                  <DropdownMenuTrigger as-child>
                    <Button class="rounded-full h-16 px-8 text-base">
                      Try the demo
                      <PhCaretDown class="ml-2 size-3.5" weight="bold" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="start" class="w-80 p-2.5">
                    <div class="flex flex-col gap-1 px-2 pt-1.5 pb-3">
                      <p class="text-lg font-semibold leading-snug tracking-tight font-display">Demo mode</p>
                      <p class="text-muted-foreground text-sm leading-relaxed">State persists in your browser only.</p>
                    </div>
                    <p class="px-2 mb-2 text-[11px] uppercase tracking-wide text-muted-foreground">Sign in as</p>
                    <div class="space-y-2">
                      <DropdownMenuItem
                        v-for="r in DEMO_ROLES"
                        :key="r.value"
                        class="items-start gap-3 p-3 rounded-lg bg-card transition-shadow focus:bg-card press"
                        :class="auth.role === r.value ? 'soft-card-selected' : 'soft-card hover:soft-card-hover'"
                        @click="loginAs(r.value)"
                      >
                        <div :class="['inline-flex size-9 items-center justify-center rounded-full shrink-0 text-white', ROLE_COLORS[r.value]]">
                          <component :is="r.icon" class="size-5" />
                        </div>
                        <div class="flex-1 min-w-0">
                          <div class="text-sm font-medium tracking-tight">{{ r.label }}</div>
                          <p class="text-xs text-muted-foreground tracking-tight mt-0.5">{{ ROLE_DESCRIPTIONS[r.value] }}</p>
                        </div>
                      </DropdownMenuItem>
                    </div>
                    <DropdownMenuItem variant="destructive" class="mt-4 gap-2 rounded-lg justify-center bg-destructive/10 hover:bg-destructive/15 focus:bg-destructive/15 py-3 font-medium press" @click="handleResetDemo">
                      <PhArrowCounterClockwise class="size-4 shrink-0" />
                      Reset demo data
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
                <Button v-else class="rounded-full h-16 px-8 text-base" @click="drawerOpen = true">
                  Try the demo
                  <PhCaretDown class="ml-2 size-3.5" weight="bold" />
                </Button>
              </template>
              <template v-else>
                <Button class="rounded-full h-16 px-8 text-base" @click="$router.push('/register')">
                  Get Started
                  <PhArrowRight class="ml-2 size-3.5" weight="bold" />
                </Button>
                <Button
                  variant="ghost"
                  class="rounded-full h-16 px-8 text-base bg-surface-inverse-foreground/10 text-surface-inverse-foreground hover:bg-surface-inverse-foreground/20 hover:text-surface-inverse-foreground"
                  @click="$router.push('/login')"
                >
                  Sign In
                </Button>
              </template>
            </div>
            <div class="flex flex-wrap items-center gap-x-5 gap-y-2 mt-8 sm:mt-10 text-xs font-medium tracking-tight text-surface-inverse-foreground/70">
              <div class="flex items-center gap-2">
                <PhStar weight="fill" class="size-3.5 text-amber-400" />
                <span>4.7 average rating</span>
              </div>
              <div class="flex items-center gap-2">
                <PhShieldCheck class="size-3.5 text-surface-inverse-foreground/90" weight="bold" />
                <span>Verified professionals</span>
              </div>
              <div class="hidden sm:flex items-center gap-2">
                <PhClock class="size-3.5 text-surface-inverse-foreground/90" weight="bold" />
                <span>Same-day service</span>
              </div>
            </div>
            </div>
            <p class="hidden lg:block lg:max-w-[15rem] text-sm leading-relaxed text-surface-inverse-foreground/55 tracking-tight">
              Book in under two minutes — no hidden fees. Pay only after the job's done, with verified pros and real reviews.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-surface-inverse">
      <div class="mx-auto max-w-7xl px-6 pb-12 sm:pb-16">
        <div v-reveal class="relative overflow-hidden rounded-3xl soft-card bg-surface-inverse">
          <img
            src="https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=2400&q=85"
            alt="A couple cooking together in their kitchen"
            class="h-[clamp(15rem,42vh,20rem)] sm:h-[clamp(28rem,70vh,44rem)] w-full object-cover object-center"
          />
          <div class="absolute inset-0 flex items-center justify-center bg-surface-inverse/20 bg-gradient-to-t from-surface-inverse/75 via-surface-inverse/30 to-surface-inverse/40">
            <div class="inline-flex items-center gap-2 rounded-full bg-white/95 px-4 py-2 text-sm font-medium tracking-tight text-gray-900 backdrop-blur soft-card">
              <PhPlay class="size-3.5" weight="fill" />
              Watch how it works
              <span class="text-gray-400">·</span>
              <span class="text-gray-500">41s</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <PopularServicesRow v-reveal :services="services" :loading="loading" />

    <HowItWorks v-reveal />

    <Testimonials v-reveal />

    <section v-reveal class="ai-surface-band">
        <div class="mx-auto max-w-7xl px-6 py-10 sm:py-16">
          <div class="mx-auto max-w-2xl text-center">
            <h2 class="font-display text-3xl sm:text-4xl font-semibold tracking-[-0.03em] mb-4 leading-[1.1] text-balance">
              Ready to book your first service?
            </h2>
            <p class="text-base text-muted-foreground mb-8 leading-relaxed mx-auto max-w-xl tracking-[-0.01em]">
              {{ DEMO
                ? "Pick a role to walk through the full booking flow. See how customers request work, how professionals accept jobs, and how admins keep the platform running."
                : "Browse verified professionals across 15+ services. Pay only after the job is done, with honest pricing and real reviews." }}
            </p>
            <div class="flex justify-center">
              <template v-if="DEMO">
                <DropdownMenu v-if="isDesktop" :modal="false">
                  <DropdownMenuTrigger as-child>
                    <Button size="lg" class="rounded-full px-7">
                      Try the demo
                      <PhCaretDown class="ml-2 size-3.5" weight="bold" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="center" class="w-72 p-1.5">
                    <div class="px-2 py-1.5 mb-1">
                      <p class="text-sm font-medium">Demo mode</p>
                      <p class="text-xs text-muted-foreground">State persists in your browser only.</p>
                    </div>
                    <DropdownMenuSeparator class="mb-1" />
                    <DropdownMenuLabel class="text-[10px] uppercase tracking-widest text-muted-foreground font-medium px-2 mb-0.5">
                      Sign in as
                    </DropdownMenuLabel>
                    <DropdownMenuItem
                      v-for="r in DEMO_ROLES"
                      :key="r.value"
                      class="gap-3 py-2 rounded-lg"
                      :class="auth.role === r.value ? 'bg-muted' : ''"
                      @click="loginAs(r.value)"
                    >
                      <div :class="['inline-flex size-8 items-center justify-center rounded-full shrink-0 text-white', ROLE_COLORS[r.value]]">
                        <component :is="r.icon" class="size-4" />
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium tracking-tight">{{ r.label }}</p>
                        <p class="text-xs text-muted-foreground tracking-tight">{{ ROLE_DESCRIPTIONS[r.value] }}</p>
                      </div>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator class="mt-1 mb-1" />
                    <DropdownMenuItem variant="destructive" class="rounded-lg" @click="handleResetDemo">
                      <PhArrowCounterClockwise class="mr-2 size-3.5" />
                      Reset demo data
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
                <Button v-else size="lg" class="rounded-full px-7" @click="drawerOpen = true">
                  Try the demo
                  <PhCaretDown class="ml-2 size-3.5" weight="bold" />
                </Button>
              </template>
              <Button v-else size="lg" class="rounded-full px-7" @click="$router.push('/register')">
                Get started
                <PhArrowRight class="ml-2 size-3.5" weight="bold" />
              </Button>
            </div>
          </div>
        </div>
      </section>

    <!-- Mobile demo sheet -->
    <ResponsiveSheet
      v-if="DEMO"
      :open="drawerOpen"
      title="Demo mode"
      description="State persists in your browser only."
      @close="drawerOpen = false"
    >
      <p class="text-[11px] uppercase tracking-wide text-muted-foreground">Sign in as</p>
      <button
        v-for="r in DEMO_ROLES"
        :key="r.value"
        class="w-full flex items-start gap-3 p-3 rounded-lg text-left press transition-shadow bg-card"
        :class="auth.role === r.value ? 'soft-card-selected' : 'soft-card hover:soft-card-hover'"
        @click="loginAs(r.value); drawerOpen = false"
      >
        <div :class="['inline-flex size-9 items-center justify-center rounded-full shrink-0 text-white', ROLE_COLORS[r.value]]">
          <component :is="r.icon" class="size-5" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-sm font-medium tracking-tight">{{ r.label }}</div>
          <p class="text-xs text-muted-foreground tracking-tight mt-0.5">{{ ROLE_DESCRIPTIONS[r.value] }}</p>
        </div>
      </button>

      <template #footer>
        <Button variant="destructive-soft" class="flex-1" @click="handleResetDemo">
          <PhArrowCounterClockwise class="size-4 shrink-0" />
          Reset demo data
        </Button>
      </template>
    </ResponsiveSheet>
  </div>
</template>

<script lang="ts" setup>
import {
  PhArrowRight,
  PhCaretDown,
  PhClock,
  PhMapPin,
  PhPlay,
  PhArrowCounterClockwise,
  PhShieldCheck,
  PhStar,
} from '@phosphor-icons/vue';
import { onMounted, ref } from "vue";
import { useMediaQuery } from "@vueuse/core";

import HowItWorks from "@/components/marketplace/HowItWorks.vue";
import PopularServicesRow from "@/components/marketplace/PopularServicesRow.vue";
import Testimonials from "@/components/marketplace/Testimonials.vue";
import { Button } from "@/components/ui/button";
import ResponsiveSheet from "@/components/ui/ResponsiveSheet.vue";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useConfirm } from "@/composables/useConfirm";
import { useDemoLogin, DEMO_ROLES } from "@/composables/useDemoLogin";
import { api } from "@/lib/api";
import { DEMO } from "@/lib/demo/flag";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const { loginAs, resetDemoData } = useDemoLogin();
const { confirm } = useConfirm();
const isDesktop = useMediaQuery("(min-width: 640px)");
const drawerOpen = ref(false);

async function handleResetDemo() {
  if (!await confirm({
    title: "Reset demo data?",
    description: "This restores the demo to its original state — any bookings, edits, or accounts you changed will be discarded.",
    variant: "destructive",
    confirmLabel: "Reset demo",
  })) return;
  drawerOpen.value = false;
  resetDemoData();
}

const ROLE_DESCRIPTIONS: Record<string, string> = {
  user: "Browse services, book professionals, and track your requests.",
  professional: "Accept jobs, set your availability, and manage your profile.",
  admin: "Manage users, approve professionals, and oversee the platform.",
};

const ROLE_COLORS: Record<string, string> = {
  user: "bg-gradient-to-b from-blue-400 to-blue-600",
  professional: "bg-gradient-to-b from-emerald-400 to-emerald-600",
  admin: "bg-gradient-to-b from-violet-400 to-violet-600",
};

interface PublicService {
  id: number;
  name: string;
  description: string | null;
  base_price: number;
  time_required: number;
  category?: string | null;
  image_url?: string;
  rating?: number;
  review_count?: number;
}

// Module-scope cache survives component unmount. Without this, navigating
// to /register and back re-runs the fetch and triggers a layout shift when
// PopularServicesRow appears mid-transition.
const cachedServices = ref<PublicService[]>([]);
let inflight: Promise<void> | null = null;

const services = cachedServices;
const loading = ref(cachedServices.value.length === 0);

onMounted(async () => {
  if (cachedServices.value.length) {
    loading.value = false;
    return;
  }
  loading.value = true;
  inflight ??= (async () => {
    try {
      const data = await api.get<PublicService[]>("/api/services");
      cachedServices.value = data.filter((s) => s.rating != null).slice(0, 6);
    } catch {
      cachedServices.value = [];
    } finally {
      inflight = null;
    }
  })();
  await inflight;
  loading.value = false;
});
</script>
