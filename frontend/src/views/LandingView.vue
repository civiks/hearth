<template>
  <div>
    <!-- Hero — full-bleed image with a left-side dark gradient scrim under the CTA copy -->
    <section
      data-public-hero
      class="relative bg-surface-inverse text-surface-inverse-foreground overflow-hidden"
    >
      <div class="relative mx-auto max-w-7xl">
        <img
          src="https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1280&q=75&auto=format&fit=crop"
          srcset="
            https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=640&q=75&auto=format&fit=crop 640w,
            https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=960&q=75&auto=format&fit=crop 960w,
            https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1280&q=75&auto=format&fit=crop 1280w,
            https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1920&q=75&auto=format&fit=crop 1920w
          "
          sizes="(max-width: 1280px) 100vw, 1280px"
          fetchpriority="high"
          decoding="async"
          alt=""
          aria-hidden="true"
          class="absolute inset-0 w-full h-full object-cover opacity-90"
        />
        <div
          class="absolute inset-0 bg-gradient-to-r from-surface-inverse from-30% via-surface-inverse/85 to-surface-inverse/20"
          aria-hidden="true"
        />
        <div
          class="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-surface-inverse via-surface-inverse/80 to-transparent"
          aria-hidden="true"
        />
        <div
          class="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-surface-inverse via-surface-inverse/70 to-transparent"
          aria-hidden="true"
        />
        <div class="relative px-6 py-24 sm:py-28 lg:py-32">
          <div class="max-w-xl">
            <div class="inline-flex items-center gap-1.5 rounded-full border border-surface-inverse-foreground/20 bg-surface-inverse-foreground/5 px-3 py-1 mb-5 sm:mb-6 text-xs font-medium tracking-tight text-surface-inverse-foreground/80 backdrop-blur">
              <MapPin class="size-3" />
              Now in Bangalore
            </div>
            <h1 class="font-display text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-[-0.03em] mb-5 sm:mb-6 leading-[1.05] text-balance">
              Home services, done right.
            </h1>
            <p class="text-base sm:text-lg text-surface-inverse-foreground/70 mb-7 sm:mb-8 max-w-lg leading-relaxed tracking-[-0.01em]">
              Verified plumbers, electricians, cleaners and more. At your doorstep within hours, with honest pricing and real reviews.
            </p>
            <div class="flex flex-wrap gap-3">
              <template v-if="DEMO">
                <DropdownMenu v-if="isDesktop" :modal="false">
                  <DropdownMenuTrigger as-child>
                    <Button size="lg">
                      Try the demo
                      <ChevronDown class="ml-2 size-3.5" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="start" class="w-64">
                    <DropdownMenuLabel>
                      <div class="flex flex-col leading-tight">
                        <span class="text-sm font-medium">Demo mode</span>
                        <span class="text-xs text-muted-foreground">
                          State persists in your browser only.
                        </span>
                      </div>
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuLabel
                      class="text-[11px] uppercase tracking-wide text-muted-foreground font-normal"
                    >
                      Sign in as
                    </DropdownMenuLabel>
                    <DropdownMenuItem
                      v-for="r in DEMO_ROLES"
                      :key="r.value"
                      :class="auth.role === r.value ? 'bg-muted font-medium' : ''"
                      @click="loginAs(r.value)"
                    >
                      <component :is="r.icon" class="mr-2 size-3.5" />
                      {{ r.label }}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem variant="destructive" @click="resetDemoData">
                      <RotateCcw class="mr-2 size-3.5" />
                      Reset demo data
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
                <Button v-else size="lg" @click="drawerOpen = true">
                  Try the demo
                  <ChevronDown class="ml-2 size-3.5" />
                </Button>
              </template>
              <template v-else>
                <Button size="lg" @click="$router.push('/register')">
                  Get Started
                  <ArrowRight class="ml-2 size-3.5" />
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  class="bg-transparent text-surface-inverse-foreground border-surface-inverse-foreground/30 hover:bg-surface-inverse-foreground/10 hover:text-surface-inverse-foreground hover:border-surface-inverse-foreground/60"
                  @click="$router.push('/login')"
                >
                  Sign In
                </Button>
              </template>
            </div>
            <div class="flex flex-wrap items-center gap-x-5 gap-y-2 mt-8 sm:mt-10 text-xs font-medium tracking-tight text-surface-inverse-foreground/70">
              <div class="flex items-center gap-2">
                <Star class="size-3.5 fill-amber-400 text-amber-400" />
                <span>4.7 average rating</span>
              </div>
              <div class="flex items-center gap-2">
                <ShieldCheck class="size-3.5 text-surface-inverse-foreground/90" />
                <span>Verified professionals</span>
              </div>
              <div class="hidden sm:flex items-center gap-2">
                <Clock class="size-3.5 text-surface-inverse-foreground/90" />
                <span>Same-day service</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <PopularServicesRow :services="services" :loading="loading" />

    <HowItWorks />

    <Testimonials />

    <section class="ai-surface-band">
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
                    <Button size="lg">
                      Try the demo
                      <ChevronDown class="ml-2 size-3.5" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="center" class="w-64">
                    <DropdownMenuLabel>
                      <div class="flex flex-col leading-tight">
                        <span class="text-sm font-medium">Demo mode</span>
                        <span class="text-xs text-muted-foreground">
                          State persists in your browser only.
                        </span>
                      </div>
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuLabel
                      class="text-[11px] uppercase tracking-wide text-muted-foreground font-normal"
                    >
                      Sign in as
                    </DropdownMenuLabel>
                    <DropdownMenuItem
                      v-for="r in DEMO_ROLES"
                      :key="r.value"
                      :class="auth.role === r.value ? 'bg-muted font-medium' : ''"
                      @click="loginAs(r.value)"
                    >
                      <component :is="r.icon" class="mr-2 size-3.5" />
                      {{ r.label }}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem variant="destructive" @click="resetDemoData">
                      <RotateCcw class="mr-2 size-3.5" />
                      Reset demo data
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
                <Button v-else size="lg" @click="drawerOpen = true">
                  Try the demo
                  <ChevronDown class="ml-2 size-3.5" />
                </Button>
              </template>
              <Button v-else size="lg" @click="$router.push('/register')">
                Get started
                <ArrowRight class="ml-2 size-3.5" />
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
        class="w-full flex items-center gap-3 p-3 rounded-lg text-left transition-shadow"
        :class="auth.role === r.value ? 'soft-card-selected' : 'bg-muted/50 hover:bg-muted'"
        @click="loginAs(r.value); drawerOpen = false"
      >
        <div :class="['inline-flex size-10 items-center justify-center rounded-full shrink-0 text-white', ROLE_COLORS[r.value]]">
          <component :is="r.icon" class="size-5" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-sm font-medium tracking-tight">{{ r.label }}</div>
          <p class="text-xs text-muted-foreground tracking-tight mt-0.5">{{ ROLE_DESCRIPTIONS[r.value] }}</p>
        </div>
      </button>

      <template #footer>
        <Button variant="destructive-soft" class="flex-1 h-11" @click="resetDemoData">
          <RotateCcw class="size-4 shrink-0" />
          Reset demo data
        </Button>
      </template>
    </ResponsiveSheet>
  </div>
</template>

<script lang="ts" setup>
import { ArrowRight, ChevronDown, Clock, MapPin, RotateCcw, ShieldCheck, Star } from "lucide-vue-next";
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
import { useDemoLogin, DEMO_ROLES } from "@/composables/useDemoLogin";
import { api } from "@/lib/api";
import { DEMO } from "@/lib/demo/flag";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const { loginAs, resetDemoData } = useDemoLogin();
const isDesktop = useMediaQuery("(min-width: 640px)");
const drawerOpen = ref(false);

const ROLE_DESCRIPTIONS: Record<string, string> = {
  user: "Browse services, book professionals, and track your requests.",
  professional: "Accept jobs, set your availability, and manage your profile.",
  admin: "Manage users, approve professionals, and oversee the platform.",
};

const ROLE_COLORS: Record<string, string> = {
  user: "bg-blue-500",
  professional: "bg-emerald-500",
  admin: "bg-violet-500",
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
