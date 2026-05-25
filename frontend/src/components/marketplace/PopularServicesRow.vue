<template>
  <section
    v-if="loading || services.length"
    class="mx-auto max-w-7xl px-6 pt-4 pb-10 sm:pt-6 sm:pb-16"
  >
    <div class="flex flex-wrap items-end justify-between gap-2 mb-6 sm:mb-8">
      <div class="min-w-0">
        <h2 class="text-2xl font-light tracking-tight">Popular services</h2>
        <p class="text-sm text-muted-foreground mt-1">
          Most-booked services in your area this month.
        </p>
      </div>
      <RouterLink
        to="/register"
        class="text-sm text-primary hover:underline underline-offset-4 inline-flex items-center gap-1 shrink-0"
      >
        See all
        <ArrowRight class="size-3.5" />
      </RouterLink>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <template v-if="services.length">
        <ServiceCard
          v-for="s in services.slice(0, 6)"
          :key="s.id"
          :service="s"
          @select="$router.push('/register')"
        />
      </template>
      <template v-else>
        <ServiceCardSkeleton v-for="i in 3" :key="`sk-${i}`" />
      </template>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { ArrowRight } from "lucide-vue-next";
import { RouterLink } from "vue-router";

import ServiceCard from "@/components/marketplace/ServiceCard.vue";
import ServiceCardSkeleton from "@/components/marketplace/ServiceCardSkeleton.vue";

withDefaults(
  defineProps<{
    services: Array<{
      id: number;
      name: string;
      description: string | null;
      base_price: number;
      time_required: number;
      category?: string | null;
      image_url?: string;
      rating?: number;
      review_count?: number;
    }>;
    loading?: boolean;
  }>(),
  { loading: false },
);
</script>
