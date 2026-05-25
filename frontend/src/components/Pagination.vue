<template>
  <PaginationRoot
    v-if="totalPages > 1"
    ref="rootEl"
    :page="page"
    :total="total"
    :items-per-page="pageSize"
    :sibling-count="1"
    show-edges
    aria-label="Pagination"
    class="flex items-center justify-center sm:justify-between gap-2 pt-2"
    @update:page="onPage"
  >
    <span class="hidden sm:inline text-xs text-muted-foreground shrink-0">{{ rangeLabel }}</span>

    <PaginationList
      v-slot="{ items }"
      class="flex items-center gap-1"
    >
      <PaginationPrev
        aria-label="Previous page"
        class="inline-flex items-center gap-1 px-2 h-7 text-xs hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors shrink-0"
      >
        <ChevronLeft class="size-3.5" />
        <span class="hidden sm:inline">Previous</span>
      </PaginationPrev>

      <template v-for="(item, idx) in items" :key="idx">
        <PaginationListItem
          v-if="item.type === 'page'"
          :value="item.value"
          class="size-7 text-xs cursor-pointer transition-colors shrink-0 hover:bg-muted data-[selected]:bg-primary data-[selected]:text-primary-foreground data-[selected]:hover:bg-primary"
        >
          {{ item.value }}
        </PaginationListItem>
        <PaginationEllipsis
          v-else
          class="size-7 inline-flex items-center justify-center text-muted-foreground shrink-0"
        >
          <MoreHorizontal class="size-3.5" />
        </PaginationEllipsis>
      </template>

      <PaginationNext
        aria-label="Next page"
        class="inline-flex items-center gap-1 px-2 h-7 text-xs hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors shrink-0"
      >
        <span class="hidden sm:inline">Next</span>
        <ChevronRight class="size-3.5" />
      </PaginationNext>
    </PaginationList>
  </PaginationRoot>
</template>

<script lang="ts" setup>
import { ChevronLeft, ChevronRight, MoreHorizontal } from "lucide-vue-next";
import {
  PaginationEllipsis,
  PaginationList,
  PaginationListItem,
  PaginationNext,
  PaginationPrev,
  PaginationRoot,
} from "reka-ui";
import { computed, nextTick, ref } from "vue";

const props = defineProps<{
  page: number;
  pageSize: number;
  total: number;
}>();
const emit = defineEmits<{ "update:page": [n: number] }>();

const rootEl = ref<{ $el: HTMLElement } | null>(null);

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.total / props.pageSize)),
);

const rangeLabel = computed(() => {
  if (!props.total) return "0 results";
  const start = (props.page - 1) * props.pageSize + 1;
  const end = Math.min(start + props.pageSize - 1, props.total);
  return `Showing ${start}–${end} of ${props.total}`;
});

function findScrollable(el: HTMLElement | null): HTMLElement | null {
  while (el && el !== document.body) {
    const { overflowY } = getComputedStyle(el);
    if (
      (overflowY === "auto" || overflowY === "scroll") &&
      el.scrollHeight > el.clientHeight
    ) {
      return el;
    }
    el = el.parentElement;
  }
  return null;
}

function onPage(n: number) {
  if (n === props.page) return;
  emit("update:page", n);
  nextTick(() => {
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const behavior: ScrollBehavior = reduce ? "auto" : "smooth";

    // Prefer the closest <section> the pagination lives in — scrolls JUST that
    // panel into view, leaving any sibling sections (hero, featured row) above.
    const navEl = rootEl.value?.$el ?? null;
    const section = navEl?.closest("section");
    if (section) {
      section.scrollIntoView({ block: "start", behavior });
      return;
    }

    // No section wrapper (e.g. admin RequestsPage uses a <div> root) — fall
    // back to scrolling the nearest scrollable ancestor to the top.
    const target =
      findScrollable(navEl) ??
      document.scrollingElement ??
      document.documentElement;
    target.scrollTo({ top: 0, behavior });
  });
}
</script>
