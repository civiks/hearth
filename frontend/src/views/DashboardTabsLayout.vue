<template>
  <div class="flex sm:h-full flex-col">
    <nav
      v-if="isDesktop"
      :class="[
        'vt-tabbar shrink-0 bg-background/80 backdrop-blur-md border-b border-border overflow-x-auto scrollbar-hide transition-shadow duration-200',
        !arrivedState.top && 'shadow-[0_2px_8px_-2px_rgb(0_0_0/0.08)]',
      ]"
      role="tablist"
    >
      <div class="mx-auto w-full max-w-[1440px] flex items-center gap-1 px-6">
        <RouterLink
          v-for="tab in tabs"
          :key="tab.to"
          :to="tab.to"
          role="tab"
          :class="[
            'flex items-center gap-2 px-2.5 py-3 -mb-px border-b-[3px] text-sm whitespace-nowrap transition-colors',
            isActive(tab.to)
              ? 'border-primary text-foreground font-medium'
              : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border',
          ]"
        >
          <component :is="tab.icon" class="size-3.5" :weight="isActive(tab.to) ? 'fill' : 'bold'" />
          {{ tab.label }}
        </RouterLink>
      </div>
    </nav>

    <div ref="contentRef" class="min-w-0 sm:flex-1 sm:overflow-auto">
      <div class="mx-auto grid w-full max-w-[1440px] grid-cols-1 [&>*]:col-start-1 [&>*]:row-start-1">
        <router-view v-slot="{ Component, route: r }">
          <Transition name="page" :appear="false">
            <component :is="Component" :key="r.path" />
          </Transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref } from "vue";
import { useMediaQuery, useScroll } from "@vueuse/core";
import { RouterLink, useRoute } from "vue-router";

import { useScrollReset } from "@/composables/useScrollReset";

const route = useRoute();
const isDesktop = useMediaQuery("(min-width: 640px)");
const contentRef = ref<HTMLElement | null>(null);
const { arrivedState } = useScroll(contentRef);
useScrollReset(contentRef);

const tabs = computed(() => route.meta.tabs as { label: string; to: string; icon: unknown }[]);

function isActive(to: string): boolean {
  return route.path === to || route.path.startsWith(`${to}/`);
}
</script>
