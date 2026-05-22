<template>
  <section v-if="featured.length" class="space-y-4">
    <header class="flex items-end justify-between gap-3">
      <div>
        <h2 class="text-lg font-medium tracking-tight inline-flex items-center gap-2">
          {{ title }}
          <component v-if="icon" :is="icon" class="size-4 text-primary" />
        </h2>
        <p v-if="subtitle" class="text-xs text-muted-foreground mt-0.5">
          {{ subtitle }}
        </p>
      </div>
      <RouterLink
        v-if="viewAllTo"
        :to="viewAllTo"
        class="inline-flex items-center gap-1 text-xs text-primary hover:underline shrink-0"
      >
        View all
        <ArrowRight class="size-3.5" />
      </RouterLink>
    </header>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      <ServiceCard
        v-for="service in featured"
        :key="service.id"
        :service="service"
        @select="$emit('select', service)"
      />
    </div>
  </section>
</template>

<script lang="ts" setup>
import { ArrowRight, TrendingUp, type LucideIcon } from "lucide-vue-next";
import { computed } from "vue";
import { RouterLink, type RouteLocationRaw } from "vue-router";

import ServiceCard from "@/components/marketplace/ServiceCard.vue";

interface Service {
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

type SortMode = "popular" | "top-rated";

const props = withDefaults(
  defineProps<{
    services: Service[];
    title?: string;
    subtitle?: string;
    icon?: LucideIcon | null;
    sortBy?: SortMode;
    limit?: number;
    viewAllTo?: RouteLocationRaw;
  }>(),
  {
    title: "Most booked this week",
    subtitle: "Top picks from your neighbors",
    icon: () => TrendingUp,
    sortBy: "popular",
    limit: 3,
  },
);
defineEmits<{ select: [service: Service] }>();

const featured = computed(() => {
  const list = [...props.services].filter((s) => s.rating != null);
  if (props.sortBy === "top-rated") {
    list.sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0));
  } else {
    list.sort((a, b) => (b.review_count ?? 0) - (a.review_count ?? 0));
  }
  return list.slice(0, props.limit);
});
</script>
