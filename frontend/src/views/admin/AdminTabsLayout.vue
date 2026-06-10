<template>
  <div class="flex sm:h-full flex-col">
    <nav
      v-if="isDesktop"
      :class="[
        'vt-tabbar shrink-0 bg-surface-inverse border-b border-surface-inverse-foreground/10 overflow-x-auto scrollbar-hide transition-shadow duration-200',
        !arrivedState.top && 'shadow-[0_2px_8px_-2px_rgb(0_0_0/0.25)]',
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
            'flex items-center gap-2 px-2.5 py-1.5 my-1.5 rounded-md text-sm whitespace-nowrap transition-colors',
            isActive(tab.to)
              ? 'bg-surface-inverse-foreground/15 text-surface-inverse-foreground font-medium'
              : 'text-surface-inverse-foreground/50 hover:bg-surface-inverse-foreground/8 hover:text-surface-inverse-foreground',
          ]"
        >
          <component :is="tab.icon" class="size-3.5" />
          {{ tab.label }}
        </RouterLink>
      </div>
    </nav>

    <div ref="contentRef" class="min-w-0 sm:flex-1 sm:overflow-auto">
      <div class="mx-auto w-full max-w-[1440px]">
        <router-view v-slot="{ Component, route: r }">
          <Transition name="page" mode="out-in" :appear="false">
            <component :is="Component" :key="r.path" />
          </Transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { useMediaQuery, useScroll } from "@vueuse/core";
import {
  Briefcase,
  ClipboardList,
  Hammer,
  LayoutDashboard,
  Users,
  Wrench,
} from "@lucide/vue";
import { RouterLink, useRoute } from "vue-router";

import { useScrollReset } from "@/composables/useScrollReset";

const route = useRoute();
const isDesktop = useMediaQuery("(min-width: 640px)");
const contentRef = ref<HTMLElement | null>(null);
const { arrivedState } = useScroll(contentRef);
useScrollReset(contentRef);

const tabs = [
  { label: "Overview",       to: "/admin/overview",      icon: LayoutDashboard },
  { label: "Services",       to: "/admin/services",      icon: Wrench },
  { label: "Professionals",  to: "/admin/professionals", icon: Briefcase },
  { label: "Users",          to: "/admin/users",         icon: Users },
  { label: "Requests",       to: "/admin/requests",      icon: ClipboardList },
  { label: "Tools",          to: "/admin/tools",         icon: Hammer },
];

function isActive(to: string): boolean {
  return route.path === to || route.path.startsWith(`${to}/`);
}
</script>
