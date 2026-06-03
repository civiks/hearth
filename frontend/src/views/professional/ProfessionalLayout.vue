<template>
  <div class="flex sm:h-full flex-col">
    <nav
      v-if="isDesktop"
      class="vt-tabbar shrink-0 bg-surface-inverse border-b border-surface-inverse-foreground/10 overflow-x-auto scrollbar-hide"
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

    <div class="min-w-0 sm:flex-1 sm:overflow-auto">
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
import { useMediaQuery } from "@vueuse/core";
import { ClipboardList, LayoutDashboard, TrendingUp } from "lucide-vue-next";
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();
const isDesktop = useMediaQuery("(min-width: 640px)");

const tabs = [
  { label: "Overview", to: "/professional/overview", icon: LayoutDashboard },
  { label: "Requests", to: "/professional/requests", icon: ClipboardList },
  { label: "Earnings", to: "/professional/earnings", icon: TrendingUp },
];

function isActive(to: string): boolean {
  return route.path === to || route.path.startsWith(`${to}/`);
}
</script>
