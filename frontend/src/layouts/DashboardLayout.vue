<template>
  <div class="flex h-screen flex-col bg-background" data-vaul-drawer-wrapper>
    <!-- Dark global top bar — brand on the left, user menu on the right -->
    <header
      class="vt-topbar flex h-12 shrink-0 items-center justify-between bg-surface-inverse px-6 text-surface-inverse-foreground relative z-20"
    >
      <RouterLink to="/" class="vt-brand flex items-center gap-2 shrink-0">
        <BrandMark class="h-4 w-auto" />
        <span class="font-semibold text-base tracking-tight">hearth</span>
      </RouterLink>

      <div class="flex items-center gap-2">
        <button
          type="button"
          aria-label="Ask AI"
          class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-inverse-foreground/10 hover:bg-surface-inverse-foreground/20 active:bg-surface-inverse-foreground/30 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-inverse-foreground/60 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-inverse text-xs font-medium"
          @click="chat.toggle()"
        >
          <span>Ask</span>
          <AiMark class="size-3.5" />
        </button>

        <!-- Desktop: popover dropdown -->
        <DropdownMenu v-if="isDesktop" :modal="false">
          <DropdownMenuTrigger as-child>
            <button
              type="button"
              class="flex items-center gap-2 px-2 py-1 rounded-full transition hover:bg-surface-inverse-foreground/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-inverse-foreground/60 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-inverse"
            >
              <Avatar class="size-6">
                <AvatarFallback class="bg-primary text-primary-foreground text-[10px]">
                  {{ initials(auth.full_name) }}
                </AvatarFallback>
              </Avatar>
              <span class="text-xs">{{ auth.email }}</span>
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
            <DropdownMenuItem v-if="DEMO" @click="resetDemoData">
              <RotateCcw class="mr-2 size-4" />
              Reset demo data
            </DropdownMenuItem>
            <DropdownMenuItem variant="destructive" @click="handleLogout">
              <LogOut class="mr-2 size-4" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <template v-else>
          <button
            type="button"
            class="flex items-center gap-2 px-2 py-1 rounded-full transition hover:bg-surface-inverse-foreground/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-inverse-foreground/60 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-inverse"
            @click="menuOpen = true"
          >
            <Avatar class="size-6">
              <AvatarFallback class="bg-primary text-primary-foreground text-[10px]">
                {{ initials(auth.full_name) }}
              </AvatarFallback>
            </Avatar>
            <span class="text-xs">{{ firstName }}</span>
            <ChevronDown class="size-3.5 opacity-70" />
          </button>

          <Drawer v-model:open="menuOpen" should-scale-background>
            <DrawerContent>
              <!-- Identity + icon shortcuts in one row -->
              <div class="flex items-center gap-2.5 px-4 pt-4 pb-3">
                <Avatar class="size-8 shrink-0">
                  <AvatarFallback class="bg-primary text-primary-foreground text-xs">
                    {{ initials(auth.full_name) }}
                  </AvatarFallback>
                </Avatar>
                <div class="flex flex-col leading-tight min-w-0 flex-1">
                  <span class="text-sm font-medium truncate">{{ auth.full_name }}</span>
                  <span class="text-xs text-muted-foreground truncate">{{ auth.email }}</span>
                </div>
                <div class="flex items-center gap-0.5 shrink-0">
                  <button
                    class="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                    aria-label="Account"
                    @click="navigate('/account')"
                  >
                    <UserCircle class="size-5" />
                  </button>
                  <button
                    class="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                    aria-label="Settings"
                    @click="navigate('/settings')"
                  >
                    <Settings class="size-5" />
                  </button>
                  <button
                    v-if="auth.role === 'admin'"
                    class="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                    aria-label="Tools"
                    @click="navigate('/admin/tools')"
                  >
                    <Hammer class="size-5" />
                  </button>
                </div>
              </div>

              <div class="overflow-y-auto p-1.5 pb-3">
                <div class="h-px bg-border -mx-1.5 mb-1.5" />

                <!-- Theme -->
                <div class="text-muted-foreground px-3 pt-2 pb-1 text-xs font-medium">Theme</div>
                <button
                  v-for="t in themeOptions"
                  :key="t.value"
                  class="w-full flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm hover:bg-accent transition-colors"
                  :class="theme === t.value ? 'bg-accent/60 text-accent-foreground' : ''"
                  @click="setTheme(t.value as Theme)"
                >
                  <component :is="t.icon" class="size-4" :class="theme === t.value ? '' : 'text-muted-foreground'" />
                  {{ t.label }}
                  <Check v-if="theme === t.value" class="ml-auto size-3.5 text-primary" />
                </button>

                <!-- Switch role (demo only) -->
                <template v-if="DEMO">
                  <div class="text-muted-foreground px-3 pt-3 pb-1 text-xs font-medium">Switch role</div>
                  <button
                    v-for="r in DEMO_ROLES"
                    :key="r.value"
                    class="w-full flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm hover:bg-accent transition-colors"
                    :class="auth.role === r.value ? 'bg-accent/60 text-accent-foreground' : ''"
                    @click="menuOpen = false; loginAs(r.value as Role)"
                  >
                    <component :is="r.icon" class="size-4" :class="auth.role === r.value ? '' : 'text-muted-foreground'" />
                    {{ r.label }}
                    <Check v-if="auth.role === r.value" class="ml-auto size-3.5 text-primary" />
                  </button>
                </template>

                <div class="h-px bg-border -mx-1.5 mt-1.5 mb-1.5" />

                <button
                  v-if="DEMO"
                  class="w-full flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm hover:bg-accent transition-colors"
                  @click="resetDemoData"
                >
                  <RotateCcw class="size-4 text-muted-foreground" />
                  Reset demo data
                </button>
                <button
                  class="w-full flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm text-destructive hover:bg-destructive/10 transition-colors"
                  @click="handleLogout"
                >
                  <LogOut class="size-4" />
                  Sign out
                </button>
              </div>
            </DrawerContent>
          </Drawer>
        </template>
      </div>
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
    <main v-else ref="scrollMain" class="flex-1 min-h-0 overflow-y-auto pb-bottom-nav">
      <slot />
    </main>
    <ChatWidget v-if="!isDesktop" mode="overlay" />

  </div>

  <!-- Teleported outside data-vaul-drawer-wrapper so CSS transform doesn't break position:fixed -->
  <Teleport to="body">
    <nav
      v-if="!isDesktop"
      class="vt-tabbar fixed bottom-0 left-0 right-0 z-40 flex border-t bg-card/95 backdrop-blur-md pb-safe"
      role="tablist"
    >
      <RouterLink
        v-for="tab in mobileTabs"
        :key="tab.to"
        :to="tab.to"
        role="tab"
        class="flex flex-1 flex-col items-center justify-center gap-1 py-3 transition-colors"
        :class="isTabActive(tab.to) ? 'text-primary' : 'text-muted-foreground'"
      >
        <component
          :is="tab.icon"
          class="size-5 transition-none"
          :stroke-width="isTabActive(tab.to) ? 2.5 : 1.75"
        />
        <span :class="auth.role === 'admin' ? 'max-[500px]:hidden text-xs font-medium leading-none' : 'text-xs font-medium leading-none'">{{ tab.label }}</span>
      </RouterLink>
      <button
        type="button"
        role="tab"
        class="flex flex-1 flex-col items-center justify-center gap-1 py-3 transition-colors"
        :class="chat.open ? 'text-primary' : 'text-muted-foreground'"
        @click="chat.toggle()"
      >
        <AiMark class="size-5" />
        <span :class="auth.role === 'admin' ? 'max-[500px]:hidden text-xs font-medium leading-none' : 'text-xs font-medium leading-none'">Ask</span>
      </button>
    </nav>
  </Teleport>
</template>

<script lang="ts" setup>
import { useMediaQuery } from "@vueuse/core";
import {
  Briefcase,
  Check,
  ChevronDown,
  ClipboardList,
  Hammer,
  LayoutDashboard,
  LayoutGrid,
  LogOut,
  Monitor,
  Moon,
  Repeat,
  RotateCcw,
  Settings,
  ShoppingBag,
  Sun,
  TrendingUp,
  UserCircle,
  Users,
  Wrench,
} from "lucide-vue-next";
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { RouterLink, useRouter, useRoute } from "vue-router";

import AiMark from "@/components/AiMark.vue";
import BrandMark from "@/components/BrandMark.vue";
import ChatWidget from "@/components/ChatWidget.vue";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Drawer, DrawerContent } from "@/components/ui/drawer";
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
const menuOpen = ref(false);

const TAB_MAP = {
  user: [
    { label: "Browse",      to: "/home/browse",    icon: ShoppingBag },
    { label: "Services",    to: "/home/services",  icon: LayoutGrid },
    { label: "My requests", to: "/home/requests",  icon: ClipboardList },
  ],
  professional: [
    { label: "Overview",  to: "/professional/overview",  icon: LayoutDashboard },
    { label: "Requests",  to: "/professional/requests",  icon: ClipboardList },
    { label: "Earnings",  to: "/professional/earnings",  icon: TrendingUp },
  ],
  admin: [
    { label: "Overview",      to: "/admin/overview",      icon: LayoutDashboard },
    { label: "Services",      to: "/admin/services",      icon: Wrench },
    { label: "Professionals", to: "/admin/professionals", icon: Briefcase },
    { label: "Users",         to: "/admin/users",         icon: Users },
    { label: "Requests",      to: "/admin/requests",      icon: ClipboardList },
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
  if (desktop) void syncChatPanel(chat.open);
});

const firstName = computed(() => auth.full_name?.split(" ")[0] ?? "");

const themeIcon = computed(() => {
  if (theme.value === "system") return Monitor;
  return effectiveTheme.value === "dark" ? Moon : Sun;
});

const themeOptions = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark",  label: "Dark",  icon: Moon },
  { value: "system", label: "System", icon: Monitor },
] as const;

function navigate(path: string) {
  menuOpen.value = false;
  router.push(path);
}

async function handleLogout() {
  menuOpen.value = false;
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
