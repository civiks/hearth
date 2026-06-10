<template>
  <section>
    <div
      class="mx-auto w-full max-w-[1440px] px-6 py-2 sm:py-3 flex flex-col sm:flex-row sm:items-center gap-4"
    >
      <div class="relative w-full sm:w-72 shrink-0">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground" />
        <Input
          :model-value="search"
          placeholder="Search for services"
          class="pl-9 h-10"
          @update:model-value="$emit('update:search', String($event))"
          @keyup.enter="$emit('submit', search)"
        />
      </div>

      <ul
        v-if="categories.length"
        class="flex gap-2 overflow-x-auto scrollbar-hide scroll-x-mask sm:flex-1 min-w-0"
      >
        <li>
          <button
            type="button"
            class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs transition-colors whitespace-nowrap"
            :class="category === null ? activeChip : inactiveChip"
            @click="$emit('update:category', null)"
          >
            All
            <span
              v-if="totalCount"
              class="inline-flex items-center justify-center min-w-[18px] rounded-full px-1 text-[10px] font-medium tabular-nums"
              :class="category === null ? 'bg-primary-foreground/20 text-primary-foreground' : 'bg-muted text-muted-foreground'"
            >
              {{ totalCount }}
            </span>
          </button>
        </li>
        <li v-for="entry in categories" :key="entry.name">
          <button
            type="button"
            class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs transition-colors whitespace-nowrap"
            :class="category === entry.name ? activeChip : inactiveChip"
            @click="$emit('update:category', entry.name)"
          >
            {{ entry.name }}
            <span
              class="inline-flex items-center justify-center min-w-[18px] rounded-full px-1 text-[10px] font-medium tabular-nums"
              :class="category === entry.name ? 'bg-primary-foreground/20 text-primary-foreground' : 'bg-muted text-muted-foreground'"
            >
              {{ entry.count }}
            </span>
          </button>
        </li>
      </ul>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { Search } from "@lucide/vue";
import { computed } from "vue";

import { Input } from "@/components/ui/input";

interface ServiceLike {
  category?: string | null;
}

const props = defineProps<{
  search: string;
  category: string | null;
  services: ServiceLike[];
}>();

defineEmits<{
  "update:search": [value: string];
  "update:category": [value: string | null];
  submit: [value: string];
}>();

const activeChip = "bg-primary text-primary-foreground border-primary";
const inactiveChip = "bg-card text-foreground border-border hover:bg-muted";

const categories = computed(() => {
  const map = new Map<string, number>();
  for (const s of props.services) {
    if (!s.category) continue;
    map.set(s.category, (map.get(s.category) ?? 0) + 1);
  }
  return [...map.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => a.name.localeCompare(b.name));
});
const totalCount = computed(() => props.services.length);
</script>
