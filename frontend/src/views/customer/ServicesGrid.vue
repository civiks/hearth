<template>
  <section class="space-y-4">
    <header class="flex items-end justify-between flex-wrap gap-2">
      <div>
        <h2 class="text-lg font-medium tracking-tight">
          {{ category ? category : "All services" }}
        </h2>
        <p class="text-xs text-muted-foreground mt-0.5">
          {{ filtered.length }} {{ filtered.length === 1 ? "service" : "services" }}
        </p>
      </div>
    </header>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
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
      :page="page"
      :page-size="pageSize"
      :total="filtered.length"
      @update:page="page = $event"
    />
  </section>
</template>

<script lang="ts" setup>
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
const pageSize = computed(() => props.pageSize ?? 8);

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
  const start = (page.value - 1) * pageSize.value;
  return filtered.value.slice(start, start + pageSize.value);
});

// Reset to page 1 whenever the filter changes
watch(
  () => [props.category, props.search],
  () => {
    page.value = 1;
  },
);
</script>
