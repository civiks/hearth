<template>
  <nav
    v-if="totalPages > 1"
    ref="rootEl"
    class="flex items-center justify-between gap-2 pt-2"
    aria-label="Pagination"
  >
    <span class="text-xs text-muted-foreground">{{ rangeLabel }}</span>

    <div class="flex items-center gap-1">
      <button
        type="button"
        class="inline-flex items-center gap-1 px-2 h-7 text-xs hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
        :disabled="page === 1"
        @click="go(Math.max(1, page - 1))"
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
            @click="go(p)"
          >
            {{ p }}
          </button>
        </li>
      </ol>

      <button
        type="button"
        class="inline-flex items-center gap-1 px-2 h-7 text-xs hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
        :disabled="page === totalPages"
        @click="go(Math.min(totalPages, page + 1))"
      >
        Next
        <ChevronRight class="size-3.5" />
      </button>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { ChevronLeft, ChevronRight } from "lucide-vue-next";
import { computed, nextTick, ref } from "vue";

const props = defineProps<{
  page: number;
  pageSize: number;
  total: number;
}>();
const emit = defineEmits<{ "update:page": [n: number] }>();

const rootEl = ref<HTMLElement | null>(null);

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

function go(n: number) {
  if (n === props.page) return;
  emit("update:page", n);
  nextTick(() => {
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const behavior: ScrollBehavior = reduce ? "auto" : "smooth";

    // Prefer the closest <section> the pagination lives in — scrolls JUST that
    // panel into view, leaving any sibling sections (hero, featured row) above.
    const section = rootEl.value?.closest("section");
    if (section) {
      section.scrollIntoView({ block: "start", behavior });
      return;
    }

    // No section wrapper (e.g. admin RequestsPage uses a <div> root) — fall
    // back to scrolling the nearest scrollable ancestor to the top.
    const target =
      findScrollable(rootEl.value) ??
      document.scrollingElement ??
      document.documentElement;
    target.scrollTo({ top: 0, behavior });
  });
}
</script>
