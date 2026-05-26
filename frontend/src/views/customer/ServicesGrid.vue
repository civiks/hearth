<template>
  <section class="space-y-4">
    <header class="flex items-end justify-between flex-wrap gap-2">
      <div>
        <h2 class="text-lg font-medium tracking-tight">
          {{ category ? category : "Services" }}
        </h2>
        <p class="text-xs text-muted-foreground mt-0.5">
          {{ filtered.length }} {{ filtered.length === 1 ? "service" : "services" }}
        </p>
      </div>
      <button
        v-if="hasMultiplePages"
        type="button"
        class="inline-flex items-center gap-1 text-xs text-primary hover:underline shrink-0 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
        @click="showAll = !showAll"
      >
        {{ showAll ? "Show less" : "View all" }}
        <ArrowRight class="size-3.5" />
      </button>
    </header>

    <div
      ref="gridEl"
      class="grid gap-3 [grid-template-columns:repeat(auto-fill,minmax(220px,1fr))]"
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

    <Pagination
      v-if="!showAll"
      :page="page"
      :page-size="pageSize"
      :total="filtered.length"
      @update:page="page = $event"
    />
  </section>
</template>

<script lang="ts" setup>
import { useElementSize } from "@vueuse/core";
import { ArrowRight } from "lucide-vue-next";
import { computed, ref, watch } from "vue";

import Pagination from "@/components/Pagination.vue";
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

const page = ref(1);
const showAll = ref(false);

// Dynamic page size: measure the grid's actual width and derive how many full
// rows of cards fit at the current viewport.
const gridEl = ref<HTMLElement | null>(null);
const { width: gridWidth } = useElementSize(gridEl);
const MIN_CARD = 220;
const GAP = 12;
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

const pageItems = computed(() => {
  if (showAll.value) return filtered.value;
  const start = (page.value - 1) * pageSize.value;
  return filtered.value.slice(start, start + pageSize.value);
});

// Whether the natural pageSize would split the list across multiple pages
const hasMultiplePages = computed(
  () => Math.ceil(filtered.value.length / pageSize.value) > 1 || showAll.value,
);

// Reset to page 1 and exit "show all" mode whenever the filter changes
watch(
  () => [props.category, props.search],
  () => {
    page.value = 1;
    showAll.value = false;
  },
);

// Clamp the current page if a viewport resize shrinks the total page count.
watch(pageSize, () => {
  const maxPage = Math.max(1, Math.ceil(filtered.value.length / pageSize.value));
  if (page.value > maxPage) page.value = maxPage;
});
</script>
