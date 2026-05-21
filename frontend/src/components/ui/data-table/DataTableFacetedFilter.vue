<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button
        variant="outline"
        size="sm"
        class="border-dashed"
        :aria-label="`Filter ${title}`"
      >
        <Filter class="size-4" :stroke-width="2" />
        <span class="ml-1.5">{{ title }}</span>
        <template v-if="selectedCount > 0">
          <span class="mx-2 h-4 w-px bg-border" aria-hidden="true" />
          <span class="text-xs">{{ selectedCount }} selected</span>
        </template>
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
import { Filter } from "lucide-vue-next";
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
