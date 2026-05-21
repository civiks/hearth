<template>
  <nav
    v-if="totalPages > 1"
    class="flex items-center justify-between gap-2 pt-2"
    aria-label="Pagination"
  >
    <span class="text-xs text-muted-foreground">{{ rangeLabel }}</span>

    <div class="flex items-center gap-1">
      <button
        type="button"
        class="inline-flex items-center gap-1 px-2 h-7 text-xs hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
        :disabled="page === 1"
        @click="$emit('update:page', Math.max(1, page - 1))"
      >
        <ChevronLeft class="size-3.5" />
        Previous
      </button>

      <ol class="flex items-center gap-1">
        <li v-for="p in totalPages" :key="p">
          <button
            type="button"
            class="size-7 text-xs cursor-pointer transition-colors"
            :class="
              p === page
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-muted'
            "
            :aria-current="p === page ? 'page' : undefined"
            @click="$emit('update:page', p)"
          >
            {{ p }}
          </button>
        </li>
      </ol>

      <button
        type="button"
        class="inline-flex items-center gap-1 px-2 h-7 text-xs hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
        :disabled="page === totalPages"
        @click="$emit('update:page', Math.min(totalPages, page + 1))"
      >
        Next
        <ChevronRight class="size-3.5" />
      </button>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { ChevronLeft, ChevronRight } from "lucide-vue-next";
import { computed } from "vue";

const props = defineProps<{
  page: number;
  pageSize: number;
  total: number;
}>();
defineEmits<{ "update:page": [n: number] }>();

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.total / props.pageSize)),
);

const rangeLabel = computed(() => {
  if (!props.total) return "0 results";
  const start = (props.page - 1) * props.pageSize + 1;
  const end = Math.min(start + props.pageSize - 1, props.total);
  return `Showing ${start}–${end} of ${props.total}`;
});
</script>
