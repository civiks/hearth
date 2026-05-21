<template>
  <Pagination
    :page="page"
    :page-size="pageSize"
    :total="total"
    @update:page="onPage"
  />
</template>

<script lang="ts" setup generic="TData">
import { computed } from "vue";
import type { Table } from "@tanstack/vue-table";

import Pagination from "@/components/Pagination.vue";

const props = defineProps<{ table: Table<TData> }>();

const state = computed(() => props.table.getState().pagination);
const page = computed(() => state.value.pageIndex + 1);
const pageSize = computed(() => state.value.pageSize);
const total = computed(() => props.table.getFilteredRowModel().rows.length);

function onPage(p: number) {
  props.table.setPageIndex(p - 1);
}
</script>
