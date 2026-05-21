<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="outline" size="sm" aria-label="Toggle columns">
        <SlidersHorizontal class="size-4" :stroke-width="2" />
        <span class="hidden sm:inline ml-1.5">View</span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-44">
      <DropdownMenuLabel class="text-xs font-medium uppercase tracking-wide">
        Toggle columns
      </DropdownMenuLabel>
      <DropdownMenuSeparator />
      <DropdownMenuCheckboxItem
        v-for="column in toggleableColumns"
        :key="column.id"
        :model-value="column.getIsVisible()"
        class="capitalize"
        @update:model-value="(v) => column.toggleVisibility(v)"
      >
        {{ columnLabel(column) }}
      </DropdownMenuCheckboxItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script lang="ts" setup generic="TData">
import { SlidersHorizontal } from "lucide-vue-next";
import { computed } from "vue";
import type { Column, Table } from "@tanstack/vue-table";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const props = defineProps<{
  table: Table<TData>;
}>();

const toggleableColumns = computed(() =>
  props.table.getAllColumns().filter((c) => c.getCanHide()),
);

function columnLabel(column: Column<TData, unknown>): string {
  const meta = column.columnDef.meta;
  if (meta?.label) return meta.label;
  const header = column.columnDef.header;
  if (typeof header === "string") return header;
  return column.id;
}
</script>
