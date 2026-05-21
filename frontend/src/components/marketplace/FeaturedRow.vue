<template>
  <section v-if="featured.length" class="space-y-4">
    <header class="flex items-end justify-between gap-3">
      <div>
        <h2 class="text-lg font-medium tracking-tight inline-flex items-center gap-2">
          Most booked this week
          <TrendingUp class="size-4 text-primary" />
        </h2>
        <p class="text-xs text-muted-foreground mt-0.5">
          Top picks from your neighbors
        </p>
      </div>
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
import { TrendingUp } from "lucide-vue-next";
import { computed } from "vue";

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

const props = defineProps<{ services: Service[] }>();
defineEmits<{ select: [service: Service] }>();

const featured = computed(() =>
  [...props.services]
    .filter((s) => s.rating != null)
    .sort((a, b) => (b.review_count ?? 0) - (a.review_count ?? 0))
    .slice(0, 3),
);
</script>
