<template>
  <div ref="rootEl" class="relative flex flex-1 min-w-0 max-w-md sm:mx-6">
    <form
      class="flex w-full items-center gap-2 h-9 px-3 rounded-full bg-foreground/6 transition-colors"
      :class="open ? 'bg-foreground/8 ring-2 ring-ring' : 'focus-within:bg-foreground/8 focus-within:ring-2 focus-within:ring-ring'"
      role="search"
      @submit.prevent="commitSearch(query)"
    >
      <PhMagnifyingGlass class="size-4 shrink-0 text-muted-foreground" weight="bold" />
      <input
        ref="inputEl"
        v-model="query"
        type="search"
        placeholder="Search services"
        aria-label="Search services"
        class="min-w-0 flex-1 bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none [&::-webkit-search-cancel-button]:hidden"
        @focus="open = true"
        @keydown.down.prevent="move(1)"
        @keydown.up.prevent="move(-1)"
      />
      <button
        v-if="query"
        type="button"
        aria-label="Clear search"
        class="shrink-0 grid place-items-center size-5 rounded-full text-muted-foreground hover:bg-foreground/10 hover:text-foreground transition-colors"
        @click="clear"
      >
        <PhX class="size-3.5" weight="bold" />
      </button>
    </form>

    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0 -translate-y-1 scale-[0.98]"
      leave-active-class="transition duration-100 ease-in"
      leave-to-class="opacity-0 -translate-y-1 scale-[0.98]"
    >
      <div
        v-if="open"
        class="z-50 origin-top rounded-2xl bg-popover text-popover-foreground soft-card border border-border/60 overflow-hidden
               fixed inset-x-3 top-[3.75rem]
               sm:absolute sm:inset-x-auto sm:top-[calc(100%+0.5rem)] sm:left-1/2 sm:-translate-x-1/2 sm:w-[30rem] sm:max-w-[calc(100vw-1.5rem)]"
      >
        <div class="max-h-[min(70vh,32rem)] overflow-y-auto scroll-fade-y py-2">
          <template v-if="query.trim()">
            <button
              type="button"
              class="flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors"
              :class="activeIndex === 0 ? 'bg-accent' : 'hover:bg-accent'"
              @mousemove="activeIndex = 0"
              @click="commitSearch(query)"
            >
              <PhMagnifyingGlass class="size-4 shrink-0 text-muted-foreground" weight="bold" />
              <span class="min-w-0 truncate text-sm tracking-tight text-muted-foreground">
                Search for <span class="font-medium text-foreground">{{ query.trim() }}</span>
              </span>
            </button>

            <p v-if="matches.length" class="px-4 pt-4 pb-1 text-[10px] font-semibold uppercase tracking-[0.1em] text-muted-foreground/70">
              Services
            </p>
            <button
              v-for="(s, i) in matches"
              :key="s.id"
              type="button"
              class="flex w-full items-baseline gap-3 px-4 py-2 text-left transition-colors"
              :class="activeIndex === i + 1 ? 'bg-accent' : 'hover:bg-accent'"
              @mousemove="activeIndex = i + 1"
              @click="selectService(s)"
            >
              <div class="min-w-0 flex-1">
                <div class="truncate text-[15px] font-medium tracking-tight text-foreground leading-tight">{{ s.name }}</div>
                <div class="truncate text-xs text-muted-foreground tracking-tight mt-0.5">{{ s.category ?? "Service" }}</div>
              </div>
              <span class="shrink-0 text-[13px] tabular-nums text-muted-foreground">₹{{ s.base_price }}</span>
            </button>

            <p v-if="!matches.length && !loading" class="px-4 py-6 text-center text-sm text-muted-foreground">
              No services match <span class="font-medium text-foreground">{{ query.trim() }}</span>.
              <br>Press Enter to search anyway.
            </p>
          </template>

          <template v-else>
            <p class="px-4 pt-1 pb-2 text-[10px] font-semibold uppercase tracking-[0.1em] text-muted-foreground/70">
              Popular searches
            </p>
            <button
              v-for="term in popular"
              :key="term"
              type="button"
              class="flex w-full items-center gap-3 px-4 py-2 text-left transition-colors hover:bg-accent"
              @click="commitSearch(term)"
            >
              <PhMagnifyingGlass class="size-3.5 shrink-0 text-muted-foreground/60" weight="bold" />
              <span class="min-w-0 truncate text-sm tracking-tight text-foreground">{{ term }}</span>
            </button>

            <p class="px-4 pt-4 pb-2 text-[10px] font-semibold uppercase tracking-[0.1em] text-muted-foreground/70">
              Browse categories
            </p>
            <button
              v-for="c in categories"
              :key="c"
              type="button"
              class="flex w-full items-center justify-between gap-3 px-4 py-2 text-left transition-colors hover:bg-accent group"
              @click="selectCategory(c)"
            >
              <span class="min-w-0 truncate text-sm font-medium tracking-tight text-foreground">{{ c }}</span>
              <PhArrowRight class="size-3.5 shrink-0 text-muted-foreground/40 transition-colors group-hover:text-muted-foreground" weight="bold" />
            </button>
          </template>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script lang="ts" setup>
import { PhArrowRight, PhMagnifyingGlass, PhX } from "@phosphor-icons/vue";
import { onClickOutside, onKeyStroke } from "@vueuse/core";
import { computed, nextTick, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { api } from "@/lib/api";
import type { Service } from "@/views/customer/ServicesGrid.vue";

const router = useRouter();
const route = useRoute();

const rootEl = ref<HTMLElement | null>(null);
const inputEl = ref<HTMLInputElement | null>(null);
const open = ref(false);
const query = ref(typeof route.query.search === "string" ? route.query.search : "");
const activeIndex = ref(-1);

const services = ref<Service[]>([]);
const loading = ref(false);
let fetched = false;

const categories = computed(() => {
  const counts = new Map<string, number>();
  for (const s of services.value) {
    if (s.category) counts.set(s.category, (counts.get(s.category) ?? 0) + 1);
  }
  return [...counts.keys()].sort((a, b) => counts.get(b)! - counts.get(a)!).slice(0, 8);
});

const popular = computed(() =>
  [...services.value]
    .filter((s) => s.name)
    .sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0) || (b.review_count ?? 0) - (a.review_count ?? 0))
    .map((s) => s.name)
    .slice(0, 6),
);

const matches = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return [];
  return services.value
    .filter((s) =>
      [s.name, s.category, s.description]
        .filter(Boolean)
        .some((f) => f!.toLowerCase().includes(q)),
    )
    .slice(0, 6);
});

const rowCount = computed(() => (query.value.trim() ? matches.value.length + 1 : 0));

async function ensureServices() {
  if (fetched) return;
  fetched = true;
  loading.value = true;
  try {
    services.value = await api.get<Service[]>("/api/services");
  } catch {
    fetched = false;
  } finally {
    loading.value = false;
  }
}

watch(open, (o) => {
  if (o) ensureServices();
  else activeIndex.value = -1;
});

watch(query, () => {
  activeIndex.value = -1;
});

watch(
  () => route.query.search,
  (s) => {
    if (!open.value) query.value = typeof s === "string" ? s : "";
  },
);

function move(delta: number) {
  open.value = true;
  if (!rowCount.value) return;
  const next = activeIndex.value + delta;
  activeIndex.value = (next + rowCount.value) % rowCount.value;
}

function close() {
  open.value = false;
  inputEl.value?.blur();
}

function commitSearch(term: string) {
  const q = term.trim();
  close();
  query.value = q;
  router.push({ path: "/home/services", query: q ? { search: q } : {} });
}

function selectService(s: Service) {
  commitSearch(s.name);
}

function selectCategory(c: string) {
  close();
  query.value = "";
  router.push({ path: "/home/services", query: { category: c } });
}

function clear() {
  query.value = "";
  inputEl.value?.focus();
}

onClickOutside(rootEl, () => (open.value = false));
onKeyStroke("Escape", () => {
  if (open.value) close();
});
onKeyStroke("Enter", (e) => {
  if (!open.value || activeIndex.value < 0) return;
  e.preventDefault();
  if (activeIndex.value === 0) commitSearch(query.value);
  else selectService(matches.value[activeIndex.value - 1]);
});

onKeyStroke("/", (e) => {
  const t = e.target as HTMLElement | null;
  if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
  e.preventDefault();
  open.value = true;
  nextTick(() => inputEl.value?.focus());
});
</script>
