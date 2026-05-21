<template>
  <div>
    <!-- Hero — full-bleed image with a left-side dark gradient scrim under the CTA copy -->
    <section
      data-public-hero
      class="relative bg-[#161616] text-white overflow-hidden"
    >
      <img
        src="https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1800&auto=format&fit=crop"
        alt=""
        aria-hidden="true"
        class="absolute inset-0 w-full h-full object-cover opacity-90"
      />
      <div
        class="absolute inset-0 bg-gradient-to-r from-[#161616] from-30% via-[#161616]/85 to-[#161616]/20"
        aria-hidden="true"
      />
      <!--
        Top-down gradient that backs the floating header. Lives INSIDE the hero
        so it scrolls with it and can never bleed into the section below.
      -->
      <div
        class="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-[#161616] via-[#161616]/80 to-transparent"
        aria-hidden="true"
      />
      <div class="relative mx-auto max-w-7xl px-6 pt-28 pb-24 lg:pt-36 lg:pb-32">
        <div class="max-w-xl">
          <div class="inline-flex items-center gap-1.5 border border-white/20 px-2 py-1 mb-6 text-xs text-white/70">
            <MapPin class="size-3" />
            Now in Bangalore
          </div>
          <h1 class="text-4xl lg:text-5xl font-light tracking-tight mb-6 leading-tight">
            Home services, done right.
          </h1>
          <p class="text-lg text-white/80 mb-8 max-w-lg">
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
              class="bg-transparent text-white border-white/30 hover:bg-white/10 hover:text-white hover:border-white/60"
              @click="$router.push('/login')"
            >
              Sign In
            </Button>
          </div>
          <div class="flex items-center gap-6 mt-10 text-xs text-white/70">
            <div class="flex items-center gap-2">
              <Star class="size-4 fill-amber-400 text-amber-400" />
              <span>4.7 average rating</span>
            </div>
            <div class="flex items-center gap-2">
              <ShieldCheck class="size-4 text-white/90" />
              <span>Verified professionals</span>
            </div>
            <div class="hidden sm:flex items-center gap-2">
              <Clock class="size-4 text-white/90" />
              <span>Same-day service</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Categories -->
    <section class="mx-auto max-w-7xl px-6 py-16">
      <h2 class="text-2xl font-light tracking-tight text-center mb-10">
        Pick a category
      </h2>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <button
          v-for="c in categories"
          :key="c.label"
          class="card-animated-border text-left bg-card p-5 flex items-center gap-3 cursor-pointer"
          @click="$router.push('/register')"
        >
          <div class="size-10 bg-primary/10 flex items-center justify-center shrink-0">
            <component :is="c.icon" class="size-5 text-primary" />
          </div>
          <span class="text-sm font-medium">{{ c.label }}</span>
        </button>
      </div>
    </section>

    <!-- Why us -->
    <section class="mx-auto max-w-7xl px-6 py-16 border-t">
      <h2 class="text-2xl font-light tracking-tight text-center mb-10">Why choose us</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <article
          v-for="f in features"
          :key="f.title"
          class="text-left bg-card p-8"
        >
          <div class="size-12 bg-primary/10 flex items-center justify-center mb-4">
            <component :is="f.icon" class="size-5 text-primary" />
          </div>
          <h3 class="text-base font-medium mb-2">{{ f.title }}</h3>
          <p class="text-sm text-muted-foreground">{{ f.body }}</p>
        </article>
      </div>
    </section>

    <!-- Popular services (live data from /api/services) -->
    <PopularServicesRow v-if="services.length" :services="services" />

    <!-- How it works -->
    <HowItWorks />

    <!-- Testimonials -->
    <Testimonials />

    <!-- CTA -->
    <section class="bg-[#161616] text-white">
      <div class="mx-auto max-w-7xl px-6 py-16 text-center">
        <h2 class="text-3xl font-light tracking-tight mb-6">
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
import {
  ArrowRight,
  Bug,
  Clock,
  Hammer,
  MapPin,
  Paintbrush,
  ShieldCheck,
  Sparkles,
  Sprout,
  Star,
  Wind,
  Wrench,
  Zap,
} from "lucide-vue-next";
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

const services = ref<PublicService[]>([]);

onMounted(async () => {
  try {
    const data = await api.get<PublicService[]>("/api/services");
    services.value = data.filter((s) => s.rating != null).slice(0, 6);
  } catch {
    services.value = [];
  }
});

const features = [
  {
    icon: ShieldCheck,
    title: "Verified Professionals",
    body: "Every service provider is thoroughly vetted and background-checked for your peace of mind.",
  },
  {
    icon: Clock,
    title: "Instant Booking",
    body: "Book services instantly with our easy-to-use platform. No more waiting for callbacks.",
  },
  {
    icon: Star,
    title: "Satisfaction Guaranteed",
    body: "Not satisfied? We'll make it right or give you a full refund. Your satisfaction is our priority.",
  },
];

const categories = [
  { icon: Wrench, label: "Plumbing" },
  { icon: Zap, label: "Electrical" },
  { icon: Hammer, label: "Carpentry" },
  { icon: Sparkles, label: "Cleaning" },
  { icon: Paintbrush, label: "Painting" },
  { icon: Wind, label: "AC & Appliance" },
  { icon: Bug, label: "Pest Control" },
  { icon: Sprout, label: "Gardening" },
];
</script>
