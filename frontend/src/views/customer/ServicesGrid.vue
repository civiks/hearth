<template>
  <section class="space-y-4">
    <h2 v-if="category" class="text-lg font-medium tracking-tight">{{ category }}</h2>

    <div
      ref="gridEl"
      class="grid gap-x-4 gap-y-6 [grid-template-columns:repeat(auto-fill,minmax(264px,1fr))]"
    >
      <ServiceCard
        v-for="service in pageItems"
        :key="service.id"
        :service="service"
        @select="$emit('select', service)"
      />
    </div>

    <div v-if="!filtered.length" class="text-center py-12 text-sm text-muted-foreground">
      No services match your search
    </div>

    <div v-if="hasMore" ref="sentinelEl" class="h-1" aria-hidden="true" />
  </section>
</template>

<script lang="ts" setup>
import { useElementSize, useIntersectionObserver } from "@vueuse/core";
import { computed, ref, watch } from "vue";

import ServiceCard from "@/components/marketplace/ServiceCard.vue";

export interface Service {
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

const props = defineProps<{
  services: Service[];
  category?: string | null;
  search?: string;
  pageSize?: number;
}>();
defineEmits<{ select: [service: Service] }>();

// Dynamic page size: measure the grid's actual width and derive how many full
// rows of cards fit at the current viewport. This drives both the initial
// reveal and each "load more" increment.
const gridEl = ref<HTMLElement | null>(null);
const { width: gridWidth } = useElementSize(gridEl);
const MIN_CARD = 264;
const GAP = 16;
const ROWS_PER_PAGE = 3;
const pageSize = computed(() => {
  if (props.pageSize) return props.pageSize;
  const w = gridWidth.value;
  if (!w) return 12; // pre-mount fallback (~4 cols × 3 rows)
  const cols = Math.max(1, Math.floor((w + GAP) / (MIN_CARD + GAP)));
  return cols * ROWS_PER_PAGE;
});

const filtered = computed(() => {
  let list = props.services;
  if (props.category) list = list.filter((s) => s.category === props.category);
  const q = (props.search ?? "").toLowerCase().trim();
  if (q) {
    list = list.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        (s.description ?? "").toLowerCase().includes(q) ||
        (s.category ?? "").toLowerCase().includes(q),
    );
  }
  return list;
});

const visibleCount = ref(pageSize.value);
const pageItems = computed(() => filtered.value.slice(0, visibleCount.value));
const hasMore = computed(() => visibleCount.value < filtered.value.length);

// Reset reveal whenever the filter changes.
watch(
  () => [props.category, props.search],
  () => { visibleCount.value = pageSize.value; },
);

// On viewport resize, never shrink the reveal — only grow it so the first
// "page" stays at least one full grid-worth.
watch(pageSize, (s) => {
  if (visibleCount.value < s) visibleCount.value = s;
});

const sentinelEl = ref<HTMLElement | null>(null);
useIntersectionObserver(
  sentinelEl,
  ([entry]) => {
    if (entry?.isIntersecting && hasMore.value) {
      visibleCount.value = Math.min(
        filtered.value.length,
        visibleCount.value + pageSize.value,
      );
    }
  },
  { rootMargin: "400px" },
);
</script>
