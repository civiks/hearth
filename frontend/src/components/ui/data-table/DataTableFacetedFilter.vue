<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button
        variant="ghost"
        size="icon"
        :aria-label="`PhFunnel ${title}`"
        :title="`PhFunnel ${title}`"
        :class="[
          'border border-border',
          selectedCount > 0 && 'text-primary hover:text-primary',
        ]"
      >
        <PhFunnel
          class="size-3.5"
          :fill="selectedCount > 0 ? 'currentColor' : 'none'"
        />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="start" class="w-52">
      <DropdownMenuLabel class="text-xs font-medium uppercase tracking-wide">
        {{ title }}
      </DropdownMenuLabel>
      <DropdownMenuSeparator />
      <DropdownMenuCheckboxItem
        v-for="opt in options"
        :key="String(opt.value)"
        :model-value="selectedValues.has(opt.value)"
        @update:model-value="(checked) => toggle(opt.value, checked)"
      >
        <span class="capitalize">{{ opt.label }}</span>
      </DropdownMenuCheckboxItem>
      <template v-if="selectedCount > 0">
        <DropdownMenuSeparator />
        <DropdownMenuItem
          class="justify-center text-xs text-muted-foreground"
          @click="clear"
        >
          Clear filters
        </DropdownMenuItem>
      </template>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script lang="ts" setup generic="TData">
import {
  PhFunnel,
} from '@phosphor-icons/vue';
import { computed } from "vue";
import type { Column } from "@tanstack/vue-table";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type FilterValue = string | number | boolean;

const props = defineProps<{
  column: Column<TData, unknown>;
  title: string;
  options: { label: string; value: FilterValue }[];
}>();

const selectedValues = computed<Set<FilterValue>>(() => {
  const v = props.column.getFilterValue() as FilterValue[] | undefined;
  return new Set(v ?? []);
});
const selectedCount = computed(() => selectedValues.value.size);

function toggle(value: FilterValue, checked: boolean) {
  const next = new Set(selectedValues.value);
  if (checked) next.add(value);
  else next.delete(value);
  props.column.setFilterValue(next.size ? Array.from(next) : undefined);
}

function clear() {
  props.column.setFilterValue(undefined);
}
</script>
