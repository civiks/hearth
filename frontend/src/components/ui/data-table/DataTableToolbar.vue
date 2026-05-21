<template>
  <div
    class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
  >
    <div class="min-w-0">
      <h2 v-if="title" class="text-base font-medium">{{ title }}</h2>
      <p v-if="description" class="text-xs text-muted-foreground">
        {{ description }}
      </p>
    </div>

    <div class="flex flex-col sm:flex-row sm:items-center gap-2">
      <div v-if="searchable" class="relative w-full sm:w-64">
        <Search
          class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground"
          :stroke-width="2"
        />
        <Input
          :model-value="globalFilter ?? ''"
          :placeholder="searchPlaceholder ?? 'Search'"
          class="pl-9"
          :aria-label="searchPlaceholder ?? 'Search'"
          @update:model-value="(v) => emit('update:globalFilter', String(v ?? ''))"
        />
      </div>

      <div v-if="filterColumns.length" class="flex flex-wrap items-center gap-2">
        <DataTableFacetedFilter
          v-for="col in filterColumns"
          :key="col.id"
          :column="col"
          :title="columnLabel(col)"
          :options="(col.columnDef.meta?.filterOptions as { label: string; value: string | number | boolean }[]) ?? []"
        />
      </div>

      <slot name="actions" />

      <DataTableViewOptions :table="table" />
    </div>
  </div>
</template>

<script lang="ts" setup generic="TData">
import { Search } from "lucide-vue-next";
import { computed } from "vue";
import type { Column, Table } from "@tanstack/vue-table";

import { Input } from "@/components/ui/input";

import DataTableFacetedFilter from "./DataTableFacetedFilter.vue";
import DataTableViewOptions from "./DataTableViewOptions.vue";

const props = defineProps<{
  table: Table<TData>;
  title?: string;
  description?: string;
  searchable?: boolean;
  searchPlaceholder?: string;
  globalFilter?: string;
}>();
const emit = defineEmits<{ "update:globalFilter": [v: string] }>();

const filterColumns = computed(() =>
  props.table
    .getAllColumns()
    .filter((c) => (c.columnDef.meta?.filterOptions?.length ?? 0) > 0),
);

function columnLabel(column: Column<TData, unknown>): string {
  const meta = column.columnDef.meta;
  if (meta?.label) return meta.label;
  const header = column.columnDef.header;
  if (typeof header === "string") return header;
  return column.id;
}
</script>
