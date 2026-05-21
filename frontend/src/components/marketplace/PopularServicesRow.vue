<template>
  <section v-if="services.length" class="mx-auto max-w-7xl px-6 py-16 border-t">
    <div class="flex items-end justify-between mb-8">
      <div>
        <h2 class="text-2xl font-light tracking-tight">Popular services</h2>
        <p class="text-sm text-muted-foreground mt-1">
          Most-booked services in your area this month.
        </p>
      </div>
      <RouterLink
        to="/register"
        class="text-sm text-primary hover:underline underline-offset-4 inline-flex items-center gap-1"
      >
        See all
        <ArrowRight class="size-3.5" />
      </RouterLink>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <ServiceCard
        v-for="s in services.slice(0, 6)"
        :key="s.id"
        :service="s"
        @select="$router.push('/register')"
      />
    </div>
  </section>
</template>

<script lang="ts" setup>
import { ArrowRight } from "lucide-vue-next";
import { RouterLink } from "vue-router";

import ServiceCard from "@/components/marketplace/ServiceCard.vue";

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
}>();
</script>
