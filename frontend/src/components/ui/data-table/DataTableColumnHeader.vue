<template>
  <button
    v-if="canSort"
    type="button"
    class="inline-flex items-center gap-1 -mx-1 px-1 h-7 hover:bg-muted text-left press transition-colors cursor-pointer text-xs font-medium uppercase tracking-wide text-muted-foreground"
    :aria-label="`Sort by ${label}`"
    @click="toggleSort"
  >
    <slot>{{ label }}</slot>
    <component
      :is="sortIcon"
      class="size-3.5 shrink-0"
      :class="isSorted ? 'text-foreground' : 'text-muted-foreground/60'"
    />
  </button>
  <span
    v-else
    class="text-xs font-medium uppercase tracking-wide text-muted-foreground"
  >
    <slot>{{ label }}</slot>
  </span>
</template>

<script lang="ts" setup generic="TData">
import {
  PhCaretDown,
  PhCaretUpDown,
  PhCaretUp,
} from '@phosphor-icons/vue';
import { computed } from "vue";
import type { Column } from "@tanstack/vue-table";

const props = defineProps<{
  column: Column<TData, unknown>;
  label: string;
}>();

const canSort = computed(() => props.column.getCanSort());
const sortDir = computed(() => props.column.getIsSorted());
const isSorted = computed(() => sortDir.value !== false);
const sortIcon = computed(() => {
  if (sortDir.value === "asc") return PhCaretUp;
  if (sortDir.value === "desc") return PhCaretDown;
  return PhCaretUpDown;
});

function toggleSort() {
  props.column.toggleSorting(props.column.getIsSorted() === "asc");
}
</script>
