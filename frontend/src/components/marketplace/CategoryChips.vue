<template>
  <section v-if="categories.length" class="border-b bg-card">
    <div class="mx-auto w-full max-w-[1440px] px-6 py-3">
      <ul class="flex flex-wrap gap-2">
        <li>
          <button
            type="button"
            class="inline-flex items-center gap-1.5 border px-3 py-1.5 text-xs transition-colors whitespace-nowrap"
            :class="
              modelValue === null
                ? activeClasses
                : inactiveClasses
            "
            @click="$emit('update:modelValue', null)"
          >
            <LayoutGrid class="size-3.5" />
            All
            <span
              v-if="totalCount"
              class="inline-flex items-center justify-center min-w-[18px] px-1 text-[10px] font-medium"
              :class="modelValue === null ? 'bg-primary-foreground/20 text-primary-foreground' : 'bg-muted text-muted-foreground'"
            >
              {{ totalCount }}
            </span>
          </button>
        </li>
        <li v-for="entry in categories" :key="entry.name">
          <button
            type="button"
            class="inline-flex items-center gap-1.5 border px-3 py-1.5 text-xs transition-colors whitespace-nowrap"
            :class="
              modelValue === entry.name
                ? activeClasses
                : inactiveClasses
            "
            @click="$emit('update:modelValue', entry.name)"
          >
            <component :is="iconFor(entry.name)" class="size-3.5" />
            {{ entry.name }}
            <span
              class="inline-flex items-center justify-center min-w-[18px] px-1 text-[10px] font-medium"
              :class="
                modelValue === entry.name
                  ? 'bg-primary-foreground/20 text-primary-foreground'
                  : 'bg-muted text-muted-foreground'
              "
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
import {
  Bug,
  Hammer,
  LayoutGrid,
  Paintbrush,
  Sparkles,
  Sprout,
  Tag,
  Wind,
  Wrench,
  Zap,
  type LucideIcon,
} from "lucide-vue-next";
import { computed } from "vue";

interface ServiceLike {
  category?: string | null;
}

const props = defineProps<{
  modelValue: string | null;
  services: ServiceLike[];
}>();
defineEmits<{ "update:modelValue": [value: string | null] }>();

// Active chip uses blue-60 (primary); inactive sits on the gray-10 card surface.
const activeClasses = "bg-primary text-primary-foreground border-primary";
const inactiveClasses = "bg-card text-foreground border-border hover:bg-muted";

const ICONS: Record<string, LucideIcon> = {
  Plumbing: Wrench,
  Electrical: Zap,
  Carpentry: Hammer,
  Cleaning: Sparkles,
  Painting: Paintbrush,
  "AC & Appliance": Wind,
  "Pest Control": Bug,
  Gardening: Sprout,
};

function iconFor(name: string): LucideIcon {
  return ICONS[name] ?? Tag;
}

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
