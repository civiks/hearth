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
        <div class="relative px-6 py-20 sm:py-24 lg:py-32">
          <div class="max-w-xl">
            <div class="inline-flex items-center gap-1.5 rounded-full border border-surface-inverse-foreground/20 bg-surface-inverse-foreground/5 px-3 py-1 mb-5 sm:mb-6 text-xs text-surface-inverse-foreground/80 backdrop-blur">
              <MapPin class="size-3" />
              Now in Bangalore
            </div>
            <h1 class="text-3xl sm:text-4xl lg:text-5xl font-light tracking-tight mb-5 sm:mb-6 leading-tight">
              Home services, done right.
            </h1>
            <p class="text-base sm:text-lg text-surface-inverse-foreground/80 font-light mb-7 sm:mb-8 max-w-lg">
              Verified plumbers, electricians, cleaners and more. At your doorstep within hours, with honest pricing and real reviews.
            </p>
            <div class="flex flex-wrap gap-3">
              <DropdownMenu v-if="DEMO" :modal="false">
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
            <div class="flex flex-wrap items-center gap-x-5 gap-y-2 mt-8 sm:mt-10 text-xs text-surface-inverse-foreground/70">
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

    <section class="ai-surface">
        <div class="mx-auto max-w-7xl px-6 py-10 sm:py-16">
          <div class="max-w-2xl">
            <h2 class="text-2xl sm:text-3xl font-medium tracking-tight mb-4">
              Ready to book your first service?
            </h2>
            <p class="text-sm sm:text-base text-muted-foreground mb-8 leading-relaxed max-w-xl">
              {{ DEMO
                ? "Pick a role to walk through the full booking flow. See how customers request work, how professionals accept jobs, and how admins keep the platform running."
                : "Browse verified professionals across 15+ services. Pay only after the job is done, with honest pricing and real reviews." }}
            </p>
            <DropdownMenu v-if="DEMO" :modal="false">
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
            <Button v-else size="lg" @click="$router.push('/register')">
              Get started
              <ArrowRight class="ml-2 size-3.5" />
            </Button>
          </div>
        </div>
      </section>
  </div>
</template>

<script lang="ts" setup>
import { ArrowRight, ChevronDown, Clock, MapPin, RotateCcw, ShieldCheck, Star } from "lucide-vue-next";
import { onMounted, ref } from "vue";

import HowItWorks from "@/components/marketplace/HowItWorks.vue";
import PopularServicesRow from "@/components/marketplace/PopularServicesRow.vue";
import Testimonials from "@/components/marketplace/Testimonials.vue";
import { Button } from "@/components/ui/button";
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
