<template>
  <div class="flex h-screen flex-col bg-background">
    <!-- Dark global top bar — brand on the left, user menu on the right -->
    <header
      class="vt-topbar flex h-12 shrink-0 items-center justify-between bg-surface-inverse px-6 text-surface-inverse-foreground relative z-20"
    >
      <RouterLink to="/" class="vt-brand flex items-center gap-2 shrink-0">
        <BrandMark class="h-4 w-auto" />
        <span class="font-semibold text-base tracking-tight">hearth</span>
      </RouterLink>

      <DropdownMenu :modal="false">
          <DropdownMenuTrigger as-child>
            <button
              type="button"
              class="flex items-center gap-2 px-2 py-1 transition hover:bg-surface-inverse-foreground/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-inverse-foreground/60 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-inverse"
            >
              <Avatar class="size-6">
                <AvatarFallback class="bg-primary text-primary-foreground text-[10px]">
                  {{ initials(auth.full_name) }}
                </AvatarFallback>
              </Avatar>
              <span class="hidden sm:inline text-xs">{{ auth.email }}</span>
              <span class="sm:hidden text-xs">{{ firstName }}</span>
              <ChevronDown class="size-3.5 opacity-70" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" class="w-56 z-[60]">
            <DropdownMenuLabel>
              <div class="flex flex-col leading-tight">
                <span class="text-sm font-medium">{{ auth.full_name }}</span>
                <span class="text-xs text-muted-foreground">{{ auth.email }}</span>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem @click="$router.push('/account')">
              <UserCircle class="mr-2 size-4" />
              Account
            </DropdownMenuItem>
            <DropdownMenuItem @click="$router.push('/settings')">
              <Settings class="mr-2 size-4" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>
                <component :is="themeIcon" class="mr-2 size-4" />
                Theme
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent class="w-40">
                <DropdownMenuRadioGroup
                  :model-value="theme"
                  @update:model-value="(v) => setTheme(v as Theme)"
                >
                  <DropdownMenuRadioItem value="light">
                    <Sun class="mr-2 size-4" />
                    Light
                  </DropdownMenuRadioItem>
                  <DropdownMenuRadioItem value="dark">
                    <Moon class="mr-2 size-4" />
                    Dark
                  </DropdownMenuRadioItem>
                  <DropdownMenuRadioItem value="system">
                    <Monitor class="mr-2 size-4" />
                    System
                  </DropdownMenuRadioItem>
                </DropdownMenuRadioGroup>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            <DropdownMenuSub v-if="DEMO">
              <DropdownMenuSubTrigger>
                <Repeat class="mr-2 size-4" />
                Switch role
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent class="w-44">
                <DropdownMenuRadioGroup
                  :model-value="auth.role ?? ''"
                  @update:model-value="(v) => loginAs(v as Role)"
                >
                  <DropdownMenuRadioItem
                    v-for="r in DEMO_ROLES"
                    :key="r.value"
                    :value="r.value"
                  >
                    <component :is="r.icon" class="mr-2 size-4" />
                    {{ r.label }}
                  </DropdownMenuRadioItem>
                </DropdownMenuRadioGroup>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              v-if="DEMO"
              @click="resetDemoData"
            >
              <RotateCcw class="mr-2 size-4" />
              Reset demo data
            </DropdownMenuItem>
            <DropdownMenuItem
              variant="destructive"
              @click="handleLogout"
            >
              <LogOut class="mr-2 size-4" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
    </header>

    <!--
      Desktop: chat docks into a Splitter as a second panel beside the route
      content. Mobile (<640px): route content takes the full width and the
      chat (when open) overlays via Teleport from ChatWidget.
    -->
    <div v-if="isDesktop" class="flex-1 min-h-0">
      <SplitterGroup
        direction="horizontal"
        :auto-save-id="CHAT_SPLITTER_ID"
      >
        <SplitterPanel :min-size="40" :order="1">
          <main ref="scrollMain" class="h-full overflow-y-auto">
            <slot />
          </main>
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
    <main v-else ref="scrollMain" class="flex-1 min-h-0 overflow-y-auto">
      <slot />
    </main>
    <ChatWidget v-if="!isDesktop" mode="overlay" />

    <!-- Floating "Ask" launcher — hidden while the panel is open. -->
    <button
      v-if="!chat.open"
      type="button"
      aria-label="Ask AI (Ctrl/Cmd+K)"
      title="Ask AI · ⌘K"
      class="fixed bottom-5 right-5 z-30 flex items-center gap-2.5 h-11 pl-5 pr-3.5 rounded-full bg-surface-inverse text-surface-inverse-foreground shadow-lg shadow-black/15 hover:bg-[#393939] active:bg-[#4c4c4c] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 dark:bg-card dark:text-foreground dark:ring-1 dark:ring-inset dark:ring-white/10 dark:shadow-black/60 dark:hover:bg-[#393939] dark:active:bg-[#525252]"
      @click="chat.toggle()"
    >
      <span class="text-sm font-medium">Ask</span>
      <AiMark class="size-5" />
    </button>
  </div>
</template>

<script lang="ts" setup>
import { useMediaQuery } from "@vueuse/core";
import {
  ChevronDown,
  LogOut,
  Monitor,
  Moon,
  Repeat,
  RotateCcw,
  Settings,
  Sun,
  UserCircle,
} from "lucide-vue-next";
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { RouterLink, useRouter, useRoute } from "vue-router";

import AiMark from "@/components/AiMark.vue";
import BrandMark from "@/components/BrandMark.vue";
import ChatWidget from "@/components/ChatWidget.vue";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  SplitterGroup,
  SplitterPanel,
  type SplitterPanelHandle,
  SplitterResizeHandle,
} from "@/components/ui/splitter";
import { useDemoLogin, DEMO_ROLES } from "@/composables/useDemoLogin";
import { useTheme, type Theme } from "@/composables/useTheme";
import { type Role } from "@/lib/api";
import { DEMO } from "@/lib/demo/flag";
import { initials } from "@/lib/format";
import { useAuthStore } from "@/stores/auth";
import {
  CHAT_DEFAULT_SIZE,
  CHAT_MAX_SIZE,
  CHAT_MIN_SIZE,
  CHAT_SPLITTER_ID,
  useChatStore,
} from "@/stores/chat";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const chat = useChatStore();
const { theme, effectiveTheme, setTheme } = useTheme();
const { loginAs, resetDemoData } = useDemoLogin();

const isDesktop = useMediaQuery("(min-width: 640px)");

const chatPanelRef = ref<SplitterPanelHandle | null>(null);
const scrollMain = ref<HTMLElement | null>(null);

watch(
  () => route.path,
  () => { scrollMain.value?.scrollTo({ top: 0, behavior: "instant" }); },
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
  // Crossing back to desktop: re-apply the chat-open state to the
  // freshly mounted splitter panel. Both branches matter — closed must
  // explicitly collapse or reka's saved layout leaves a ghost panel.
  if (desktop) void syncChatPanel(chat.open);
});

const firstName = computed(() => auth.full_name?.split(" ")[0] ?? "");

const themeIcon = computed(() => {
  if (theme.value === "system") return Monitor;
  return effectiveTheme.value === "dark" ? Moon : Sun;
});

async function handleLogout() {
  await auth.logout();
  router.push("/");
}

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
  // Sync chat-open state into the splitter on initial mount AND across
  // HMR/relogin. Reka persists the panel layout via `autoSaveId`, so on
  // mount it may restore the user's last width (e.g. 28%) even though the
  // store's `chat.open` is false — leaving a ghost empty panel. Always
  // call syncChatPanel so the closed case explicitly collapses.
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
