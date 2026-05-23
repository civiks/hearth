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
        <div class="relative px-6 py-20 sm:py-24 lg:py-32">
          <div class="max-w-xl">
            <div class="inline-flex items-center gap-1.5 border border-surface-inverse-foreground/20 px-2 py-1 mb-5 sm:mb-6 text-xs text-surface-inverse-foreground/70">
              <MapPin class="size-3" />
              Now in Bangalore
            </div>
            <h1 class="text-3xl sm:text-4xl lg:text-5xl font-light tracking-tight mb-5 sm:mb-6 leading-tight">
              Home services, done right.
            </h1>
            <p class="text-base sm:text-lg text-surface-inverse-foreground/80 mb-7 sm:mb-8 max-w-lg">
              Plumbers, electricians, cleaners and more — verified pros at your
              doorstep within hours. Honest pricing, real reviews.
            </p>
            <div class="flex flex-wrap gap-3">
              <Button size="lg" @click="$router.push('/register')">
                Get Started
                <ArrowRight class="ml-2 size-4" />
              </Button>
              <Button
                variant="outline"
                size="lg"
                class="bg-transparent text-surface-inverse-foreground border-surface-inverse-foreground/30 hover:bg-surface-inverse-foreground/10 hover:text-surface-inverse-foreground hover:border-surface-inverse-foreground/60"
                @click="$router.push('/login')"
              >
                Sign In
              </Button>
            </div>
            <div class="flex flex-wrap items-center gap-x-5 gap-y-2 mt-8 sm:mt-10 text-xs text-surface-inverse-foreground/70">
              <div class="flex items-center gap-2">
                <Star class="size-4 fill-amber-400 text-amber-400" />
                <span>4.7 average rating</span>
              </div>
              <div class="flex items-center gap-2">
                <ShieldCheck class="size-4 text-surface-inverse-foreground/90" />
                <span>Verified professionals</span>
              </div>
              <div class="hidden sm:flex items-center gap-2">
                <Clock class="size-4 text-surface-inverse-foreground/90" />
                <span>Same-day service</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Popular services (live data from /api/services) -->
    <PopularServicesRow :services="services" :loading="loading" />

    <!-- How it works -->
    <HowItWorks />

    <!-- Testimonials -->
    <Testimonials />

    <!-- CTA -->
    <section class="bg-surface-inverse text-surface-inverse-foreground">
      <div class="mx-auto max-w-7xl px-6 py-12 sm:py-16 text-center">
        <h2 class="text-2xl sm:text-3xl font-light tracking-tight mb-5 sm:mb-6">
          Ready to book your first service?
        </h2>
        <Button size="lg" @click="$router.push('/register')">
          Get Started Today
          <ArrowRight class="ml-2 size-4" />
        </Button>
      </div>
    </section>
  </div>
</template>

<script lang="ts" setup>
import { ArrowRight, Clock, MapPin, ShieldCheck, Star } from "lucide-vue-next";
import { onMounted, ref } from "vue";

import HowItWorks from "@/components/marketplace/HowItWorks.vue";
import PopularServicesRow from "@/components/marketplace/PopularServicesRow.vue";
import Testimonials from "@/components/marketplace/Testimonials.vue";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

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
