<template>
  <section class="flex flex-col gap-4 sm:min-h-[640px] min-w-0">
    <DataTableToolbar
      :table="table"
      :title="title"
      :description="description"
      :searchable="searchable"
      :search-placeholder="searchPlaceholder"
      :global-filter="globalFilter"
      @update:global-filter="setGlobalFilter"
    >
      <template v-if="$slots.actions" #actions>
        <slot name="actions" />
      </template>
    </DataTableToolbar>

    <div class="flex-1 overflow-y-auto min-w-0">
      <Table>
      <TableHeader>
        <TableRow
          v-for="hg in table.getHeaderGroups()"
          :key="hg.id"
          class="hover:bg-transparent"
        >
          <TableHead
            v-for="header in hg.headers"
            :key="header.id"
            :class="[
              header.column.columnDef.meta?.align === 'right' ? 'text-right' : '',
              header.column.columnDef.meta?.align === 'center' ? 'text-center' : '',
              (header.column.columnDef.meta as { headClass?: string } | undefined)?.headClass ?? '',
            ]"
            :style="header.id === 'actions' ? 'width: 3rem' : undefined"
          >
            <template v-if="!header.isPlaceholder">
              <DataTableColumnHeader
                v-if="header.column.getCanSort()"
                :column="header.column"
                :label="headerLabel(header)"
              />
              <span v-else class="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                <FlexRender :render="header.column.columnDef.header" :props="header.getContext()" />
              </span>
            </template>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow
          v-for="row in table.getRowModel().rows"
          :key="row.id"
          :class="row.index % 2 === 1 ? 'bg-muted/30' : ''"
        >
          <TableCell
            v-for="cell in row.getVisibleCells()"
            :key="cell.id"
            :class="[
              cell.column.columnDef.meta?.nowrap ? 'whitespace-nowrap' : 'truncate',
              cell.column.columnDef.meta?.align === 'right' ? 'text-right' : '',
              cell.column.columnDef.meta?.align === 'center' ? 'text-center' : '',
              cell.column.columnDef.meta?.cellClass ?? '',
              cell.column.columnDef.meta?.mono ? 'font-mono tabular-nums' : '',
            ]"
          >
            <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

      <DataTableEmpty
        v-if="!loading && !totalRows"
        :message="emptyMessage ?? 'No matching results'"
      />
    </div>

    <div v-if="totalRows" class="sm:sticky sm:bottom-0 border-t bg-background px-6 pt-3 pb-3">
      <DataTablePagination :table="table" />
    </div>
  </section>
</template>

<script lang="ts" setup generic="TData">
import {
  FlexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useVueTable,
  type ColumnDef,
  type ColumnFiltersState,
  type Header,
  type SortingState,
  type VisibilityState,
} from "@tanstack/vue-table";
import { computed, ref, watch } from "vue";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import DataTableColumnHeader from "./DataTableColumnHeader.vue";
import DataTableEmpty from "./DataTableEmpty.vue";
import DataTablePagination from "./DataTablePagination.vue";
import DataTableToolbar from "./DataTableToolbar.vue";

const props = withDefaults(
  defineProps<{
    columns: ColumnDef<TData, unknown>[];
    data: TData[];
    title?: string;
    description?: string;
    searchable?: boolean;
    searchPlaceholder?: string;
    /** Override the field used for global search. If omitted, search runs across all string cells. */
    globalFilterAccessor?: (row: TData) => string;
    pageSize?: number;
    emptyMessage?: string;
    loading?: boolean;
  }>(),
  {
    searchable: true,
    pageSize: 10,
  },
);

const sorting = ref<SortingState>([]);
const columnFilters = ref<ColumnFiltersState>([]);
const columnVisibility = ref<VisibilityState>({});
const globalFilter = ref("");

const table = useVueTable({
  get data() {
    return props.data;
  },
  get columns() {
    return props.columns;
  },
  state: {
    get sorting() {
      return sorting.value;
    },
    get columnFilters() {
      return columnFilters.value;
    },
    get columnVisibility() {
      return columnVisibility.value;
    },
    get globalFilter() {
      return globalFilter.value;
    },
  },
  initialState: {
    pagination: {
      pageSize: props.pageSize,
      pageIndex: 0,
    },
  },
  onSortingChange: (updater) => {
    sorting.value =
      typeof updater === "function" ? updater(sorting.value) : updater;
  },
  onColumnFiltersChange: (updater) => {
    columnFilters.value =
      typeof updater === "function" ? updater(columnFilters.value) : updater;
  },
  onColumnVisibilityChange: (updater) => {
    columnVisibility.value =
      typeof updater === "function" ? updater(columnVisibility.value) : updater;
  },
  onGlobalFilterChange: (updater) => {
    globalFilter.value =
      typeof updater === "function" ? updater(globalFilter.value) : updater;
  },
  globalFilterFn: (row, _columnId, filterValue) => {
    if (!filterValue) return true;
    const q = String(filterValue).toLowerCase().trim();
    if (!q) return true;
    if (props.globalFilterAccessor) {
      return props.globalFilterAccessor(row.original).toLowerCase().includes(q);
    }
    // Default: stringify all cells and search across them
    return row
      .getVisibleCells()
      .some((cell) => {
        const v = cell.getValue();
        if (v == null) return false;
        return String(v).toLowerCase().includes(q);
      });
  },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  filterFns: {},
});

const totalRows = computed(() => table.getFilteredRowModel().rows.length);

// When filters change, reset to page 1
watch(
  () => [globalFilter.value, columnFilters.value],
  () => {
    table.setPageIndex(0);
  },
  { deep: true },
);

function setGlobalFilter(v: string) {
  globalFilter.value = v;
}

function headerLabel(header: Header<TData, unknown>): string {
  const meta = header.column.columnDef.meta;
  if (meta?.label) return meta.label;
  const h = header.column.columnDef.header;
  if (typeof h === "string") return h;
  return header.column.id;
}
</script>
