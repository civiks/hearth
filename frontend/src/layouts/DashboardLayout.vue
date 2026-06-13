<template>
  <div class="flex min-h-dvh sm:h-dvh flex-col bg-background">
    <div v-if="isDesktop" class="flex-1 min-h-0">
      <SplitterGroup
        direction="horizontal"
        :auto-save-id="CHAT_SPLITTER_ID"
      >
        <SplitterPanel :min-size="40" :order="1">
          <div class="flex h-full flex-col">
            <DashboardTopbar />
            <main ref="scrollMain" class="flex-1 min-h-0 overflow-y-auto">
              <slot />
            </main>
          </div>
        </SplitterPanel>
        <SplitterResizeHandle
          v-show="chat.open"
          class="chat-handle-transition"
        />
        <!--
          Chat panel is always mounted but starts collapsed (size=0). On
          chat.open it imperatively expands/collapses; the `chat-panel` class
          adds a CSS transition on flex-grow so the change animates. The
          inner ChatWidget only renders while open to keep its state lazy.
        -->
        <SplitterPanel
          ref="chatPanelRef"
          id="chat-pane"
          collapsible
          :default-size="0"
          :collapsed-size="0"
          :min-size="CHAT_MIN_SIZE"
          :max-size="CHAT_MAX_SIZE"
          :order="2"
          class="chat-panel"
        >
          <ChatWidget v-if="chat.open" mode="inline" />
        </SplitterPanel>
      </SplitterGroup>
    </div>
    <template v-else>
      <DashboardTopbar />
      <main ref="scrollMain" class="flex-1 pb-bottom-nav">
        <slot />
      </main>
      <ChatWidget mode="overlay" />
    </template>

  </div>

  <SettingsDrawer />

  <!-- Teleported outside data-vaul-drawer-wrapper so CSS transform doesn't break position:fixed -->
  <Teleport to="body">
    <nav
      ref="tabbarRef"
      v-if="!isDesktop"
      class="vt-tabbar fixed bottom-0 left-0 right-0 z-40 flex overflow-x-auto scrollbar-hide border-t border-border/50 bg-card/80 backdrop-blur-xl pb-safe"
      role="tablist"
    >
      <RouterLink
        v-for="tab in mobileTabs"
        :key="tab.to"
        :to="tab.to"
        role="tab"
        :class="[
          'flex flex-1 min-w-[72px] flex-col items-center justify-center gap-1 py-3 transition-colors',
          isTabActive(tab.to) ? 'text-foreground' : 'text-muted-foreground',
        ]"
      >
        <span
          :class="[
            'flex items-center justify-center rounded-full px-4 py-1 transition-colors',
            isTabActive(tab.to) ? 'bg-primary/10' : '',
          ]"
        >
          <component :is="tab.icon" class="size-5 transition-none" :weight="isTabActive(tab.to) ? 'fill' : 'bold'" />
        </span>
        <span :class="['text-xs leading-none', isTabActive(tab.to) ? 'font-semibold' : 'font-medium']">{{ tab.label }}</span>
      </RouterLink>
      <button
        type="button"
        role="tab"
        :class="[
          'flex flex-1 min-w-[72px] flex-col items-center justify-center gap-1 py-3 transition-colors',
          chat.open ? 'text-foreground' : 'text-muted-foreground',
        ]"
        @click="chat.toggle()"
      >
        <span
          :class="[
            'flex items-center justify-center rounded-full px-4 py-1 transition-colors',
            chat.open ? 'bg-primary/10' : '',
          ]"
        >
          <AiMark class="size-5" />
        </span>
        <span :class="['text-xs leading-none', chat.open ? 'font-semibold' : 'font-medium']">Ask</span>
      </button>

      <div v-if="canScrollRight" class="pointer-events-none absolute inset-y-0 right-0 flex items-center">
        <div class="absolute inset-y-0 right-0 w-14 bg-gradient-to-l from-card/80 to-transparent" />
        <button
          type="button"
          class="relative pointer-events-auto z-10 mr-2 flex size-9 items-center justify-center rounded-full border border-border bg-card text-muted-foreground shadow-sm"
          @click="scrollTabbar"
        >
          <PhCaretRight class="size-4" />
        </button>
      </div>
    </nav>
  </Teleport>
</template>

<script lang="ts" setup>
import { useElementSize, useMediaQuery, useScroll } from "@vueuse/core";
import {
  PhBriefcase,
  PhCaretRight,
  PhClipboardText,
  PhSquaresFour,
  PhGridFour,
  PhShoppingBag,
  PhTrendUp,
  PhUsers,
  PhWrench,
} from '@phosphor-icons/vue';
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";

import AiMark from "@/components/AiMark.vue";
import ChatWidget from "@/components/ChatWidget.vue";
import DashboardTopbar from "@/components/DashboardTopbar.vue";
import SettingsDrawer from "@/components/SettingsDrawer.vue";
import {
  SplitterGroup,
  SplitterPanel,
  type SplitterPanelHandle,
  SplitterResizeHandle,
} from "@/components/ui/splitter";
import { useAuthStore } from "@/stores/auth";
import {
  CHAT_DEFAULT_SIZE,
  CHAT_MAX_SIZE,
  CHAT_MIN_SIZE,
  CHAT_SPLITTER_ID,
  useChatStore,
} from "@/stores/chat";

const route = useRoute();
const auth = useAuthStore();
const chat = useChatStore();

const isDesktop = useMediaQuery("(min-width: 640px)");

const tabbarRef = ref<HTMLElement | null>(null);
const { width: tabbarWidth } = useElementSize(tabbarRef);
const { arrivedState } = useScroll(tabbarRef);
const canScrollRight = computed(() => {
  const el = tabbarRef.value;
  if (!el || tabbarWidth.value === 0) return false;
  return el.scrollWidth > el.clientWidth && !arrivedState.right;
});
function scrollTabbar() {
  tabbarRef.value?.scrollBy({ left: 120, behavior: "smooth" });
}

const TAB_MAP = {
  user: [
    { label: "Browse",      to: "/home/browse",    icon: PhShoppingBag },
    { label: "Services",    to: "/home/services",  icon: PhGridFour },
    { label: "My requests", to: "/home/requests",  icon: PhClipboardText },
  ],
  professional: [
    { label: "Overview",  to: "/professional/overview",  icon: PhSquaresFour },
    { label: "Requests",  to: "/professional/requests",  icon: PhClipboardText },
    { label: "Earnings",  to: "/professional/earnings",  icon: PhTrendUp },
  ],
  admin: [
    { label: "Overview",      to: "/admin/overview",      icon: PhSquaresFour },
    { label: "Services",      to: "/admin/services",      icon: PhWrench },
    { label: "Professionals", to: "/admin/professionals", icon: PhBriefcase },
    { label: "Users",           to: "/admin/users",         icon: PhUsers },
    { label: "Requests",      to: "/admin/requests",      icon: PhClipboardText },
  ],
} as const;

const mobileTabs = computed(() => TAB_MAP[auth.role as keyof typeof TAB_MAP] ?? []);

function isTabActive(to: string) {
  return route.path === to || route.path.startsWith(`${to}/`);
}

const chatPanelRef = ref<SplitterPanelHandle | null>(null);
const scrollMain = ref<HTMLElement | null>(null);

watch(
  () => route.path,
  () => {
    scrollMain.value?.scrollTo({ top: 0, behavior: "instant" });
  },
);

async function syncChatPanel(open: boolean) {
  await nextTick();
  const p = chatPanelRef.value;
  if (!p) return;
  if (open) {
    p.expand();
    if (Math.abs(p.getSize() - CHAT_MIN_SIZE) < 0.5) {
      p.resize(CHAT_DEFAULT_SIZE);
    }
  } else {
    p.collapse();
  }
}

watch(() => chat.open, syncChatPanel);
watch(isDesktop, (desktop) => {
  if (desktop) void syncChatPanel(chat.open);
});

// Global Cmd/Ctrl+K toggles the chat from anywhere; Esc closes it when open.
function onGlobalKey(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    chat.toggle();
    return;
  }
  if (e.key === "Escape" && chat.open) {
    chat.close();
  }
}
onMounted(() => {
  window.addEventListener("keydown", onGlobalKey);
  if (isDesktop.value) void syncChatPanel(chat.open);
});
onBeforeUnmount(() => window.removeEventListener("keydown", onGlobalKey));
</script>

<style scoped>
.chat-panel {
  transition: flex 180ms cubic-bezier(0.16, 1, 0.3, 1);
}
.chat-handle-transition {
  transition: opacity 150ms ease-out;
}
</style>
