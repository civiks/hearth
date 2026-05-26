<template>
  <div class="flex h-full flex-col">
    <!-- Desktop: full horizontal tab strip -->
    <nav
      v-if="isDesktop"
      class="vt-tabbar flex shrink-0 items-center gap-1 border-b bg-card px-6 overflow-x-auto scrollbar-hide"
      role="tablist"
    >
      <RouterLink
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        role="tab"
        :class="[
          'relative -mb-px flex items-center gap-2 px-3 py-3 text-sm whitespace-nowrap transition-colors',
          isActive(tab.to)
            ? 'text-foreground border-b-2 border-primary font-medium'
            : 'text-muted-foreground hover:text-foreground border-b-2 border-transparent',
        ]"
      >
        <component :is="tab.icon" class="size-4" />
        {{ tab.label }}
      </RouterLink>
    </nav>

    <div class="flex-1 min-w-0 overflow-auto">
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
import {
  Briefcase,
  ClipboardList,
  Hammer,
  LayoutDashboard,
  Users,
  Wrench,
} from "lucide-vue-next";
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();
const isDesktop = useMediaQuery("(min-width: 640px)");

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
