<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-150"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="chat.open && !isDesktop"
        class="fixed inset-0 z-40 bg-black/40 sm:hidden"
        aria-hidden="true"
        @click="chat.close()"
      />
    </Transition>

    <Transition
      enter-active-class="transition-transform duration-200 ease-out"
      leave-active-class="transition-transform duration-150 ease-in"
      enter-from-class="translate-x-full"
      leave-to-class="translate-x-full"
    >
      <aside
        v-if="chat.open"
        class="fixed z-50 flex flex-col bg-background shadow-2xl sm:top-12 inset-0 sm:left-auto sm:right-0 sm:bottom-0 ai-surface ai-outline"
        :style="panelStyle"
        role="dialog"
        aria-label="Assistant"
      >
        <!-- Resize handle (desktop only, left edge) -->
        <div
          class="hidden sm:block absolute top-0 left-0 bottom-0 w-1 -translate-x-1/2 cursor-ew-resize group z-10"
          @mousedown="onResizeStart"
        >
          <div
            class="absolute inset-y-0 left-1/2 -translate-x-1/2 w-px bg-transparent group-hover:bg-primary/60 transition-colors"
            :class="resizing && 'bg-primary/60'"
          />
        </div>

        <!-- Header — name (with model picker) left, actions right -->
        <header class="flex h-11 shrink-0 items-center justify-between border-b pl-2 pr-2 bg-background/80 backdrop-blur">
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <button
                type="button"
                class="flex items-center gap-1 px-2 h-8 text-sm font-medium hover:bg-muted transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                :title="`Model: ${chat.currentModel.name}`"
              >
                hearth AI
                <ChevronDown class="size-3.5 opacity-60" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" class="w-64">
              <DropdownMenuLabel class="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
                Model
              </DropdownMenuLabel>
              <DropdownMenuRadioGroup
                :model-value="chat.modelId"
                @update:model-value="(v) => chat.setModel(v as string)"
              >
                <DropdownMenuRadioItem
                  v-for="m in CHAT_MODELS"
                  :key="m.id"
                  :value="m.id"
                  class="gap-2.5 items-start py-2"
                >
                  <span
                    class="size-2.5 rounded-full shrink-0 mt-1"
                    :style="{ background: m.color }"
                    aria-hidden="true"
                  />
                  <div class="flex-1 min-w-0">
                    <div class="text-sm font-medium leading-tight">{{ m.name }}</div>
                    <div class="text-xs text-muted-foreground">
                      {{ m.provider }} · {{ m.tagline }}
                    </div>
                  </div>
                </DropdownMenuRadioItem>
              </DropdownMenuRadioGroup>
            </DropdownMenuContent>
          </DropdownMenu>

          <div class="flex items-center gap-0.5">
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <button
                  type="button"
                  class="size-8 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                  aria-label="Conversation history"
                >
                  <History class="size-4" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" class="w-72 max-h-80 overflow-y-auto">
                <DropdownMenuLabel class="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
                  Past conversations
                </DropdownMenuLabel>
                <div
                  v-if="chat.sortedConversations.length === 0"
                  class="px-2 py-4 text-xs text-muted-foreground text-center"
                >
                  No past conversations yet.
                </div>
                <DropdownMenuItem
                  v-for="c in chat.sortedConversations"
                  :key="c.id"
                  class="gap-2 items-start py-2 group"
                  :class="c.id === chat.currentConversationId && 'bg-muted/60'"
                  @click.stop="onLoadConversation(c.id)"
                >
                  <div class="flex-1 min-w-0">
                    <div class="text-sm leading-tight truncate">{{ c.title }}</div>
                    <div class="text-[10px] text-muted-foreground mt-0.5">
                      {{ formatRelative(c.updatedAt) }}
                    </div>
                  </div>
                  <button
                    type="button"
                    class="opacity-0 group-hover:opacity-100 p-1 -m-1 text-muted-foreground hover:text-destructive transition"
                    aria-label="Delete conversation"
                    @click.stop="chat.deleteConversation(c.id)"
                  >
                    <Trash2 class="size-3.5" />
                  </button>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button
              variant="ghost"
              size="icon"
              class="size-8"
              aria-label="New conversation"
              :disabled="!chat.hasMessages && !chat.streaming"
              @click="chat.startNew()"
            >
              <Plus class="size-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              class="size-8"
              aria-label="Close"
              @click="chat.close()"
            >
              <X class="size-4" />
            </Button>
          </div>
        </header>

        <!-- Messages -->
        <div
          ref="scrollEl"
          class="flex-1 overflow-y-auto px-4 py-4 space-y-5 scroll-fade"
        >
          <!-- Empty state -->
          <div v-if="!chat.hasMessages" class="space-y-5 pt-2">
            <AiMark class="size-9" />
            <p class="text-sm text-muted-foreground leading-relaxed">
              Ask anything about {{ roleScopeLabel }}. I can call tools to fetch real data
              from your account.
            </p>
            <div class="space-y-1.5">
              <div class="text-[11px] font-medium text-muted-foreground uppercase tracking-wide">
                Try
              </div>
              <div class="flex flex-col gap-1.5">
                <button
                  v-for="p in suggestedPrompts"
                  :key="p"
                  type="button"
                  class="text-left text-sm border border-primary/30 text-primary hover:bg-primary/5 px-3 py-1.5 rounded-full transition w-fit"
                  @click="onSuggested(p)"
                >
                  {{ p }}
                </button>
              </div>
            </div>
          </div>

          <!-- Messages -->
          <template v-for="m in chat.messages" :key="m.id">
            <!-- User turn — right-aligned grey bubble, time below -->
            <div v-if="m.role === 'user'" class="space-y-0.5">
              <div class="flex justify-end">
                <div class="text-sm bg-muted px-3 py-2 rounded-lg rounded-tr-sm max-w-[85%] whitespace-pre-wrap break-words">
                  {{ m.text }}
                </div>
              </div>
              <div class="text-[10px] text-muted-foreground text-right">
                {{ formatTime(m.timestamp) }}
              </div>
            </div>

            <!-- Assistant turn — avatar + name + time, body indented -->
            <div v-else class="space-y-1.5">
              <div class="flex items-center gap-2 text-[11px]">
                <AiMark class="size-5" />
                <span class="font-medium">hearth AI</span>
                <span class="text-muted-foreground">{{ formatTime(m.timestamp) }}</span>
              </div>

              <div class="space-y-2">
                <details
                  v-for="tc in m.toolCalls"
                  :key="tc.id"
                  class="text-xs border bg-card/60 ai-surface-soft"
                >
                  <summary
                    class="cursor-pointer px-2.5 py-1.5 flex items-center gap-2 select-none"
                  >
                    <Loader2
                      v-if="tc.status === 'running'"
                      class="size-3 shrink-0 animate-spin text-muted-foreground"
                    />
                    <CheckCircle2
                      v-else-if="tc.status === 'ok'"
                      class="size-3 shrink-0 text-emerald-600"
                    />
                    <AlertCircle
                      v-else
                      class="size-3 shrink-0 text-red-600"
                    />
                    <span class="truncate">
                      {{ labelForTool(auth.role, tc.name, tc.args) }}
                      <span
                        v-if="tc.status === 'ok' && resultSummary(tc.result)"
                        class="text-muted-foreground ml-1"
                      >
                        · {{ resultSummary(tc.result) }}
                      </span>
                    </span>
                  </summary>
                  <pre
                    class="px-2.5 pb-2 pt-1 text-[11px] leading-snug whitespace-pre-wrap break-words text-muted-foreground max-h-48 overflow-y-auto"
                  >{{ formatResult(tc.result, tc.status) }}</pre>
                </details>

                <div
                  v-if="m.text || m.pending"
                  class="text-sm leading-relaxed"
                  v-html="renderMarkdownish(m.text)"
                />
                <span
                  v-if="m.pending && !m.text && m.toolCalls.length === 0"
                  class="inline-flex gap-1"
                  aria-label="Thinking"
                >
                  <span class="size-1.5 rounded-full bg-muted-foreground/60 animate-pulse" />
                  <span class="size-1.5 rounded-full bg-muted-foreground/60 animate-pulse" style="animation-delay: 120ms" />
                  <span class="size-1.5 rounded-full bg-muted-foreground/60 animate-pulse" style="animation-delay: 240ms" />
                </span>

                <!-- Feedback row -->
                <div
                  v-if="!m.pending && m.text"
                  class="flex items-center gap-0.5 pt-1 -ml-1.5"
                >
                  <button
                    type="button"
                    class="p-1.5 text-muted-foreground hover:text-foreground transition rounded"
                    :class="m.feedback === 'up' && 'text-primary'"
                    aria-label="Helpful"
                    @click="chat.setFeedback(m.id, 'up')"
                  >
                    <ThumbsUp class="size-3.5" />
                  </button>
                  <button
                    type="button"
                    class="p-1.5 text-muted-foreground hover:text-foreground transition rounded"
                    :class="m.feedback === 'down' && 'text-destructive'"
                    aria-label="Not helpful"
                    @click="chat.setFeedback(m.id, 'down')"
                  >
                    <ThumbsDown class="size-3.5" />
                  </button>
                  <button
                    type="button"
                    class="p-1.5 text-muted-foreground hover:text-foreground transition rounded disabled:opacity-50"
                    aria-label="Regenerate"
                    :disabled="chat.streaming"
                    @click="onRegenerate(m.id)"
                  >
                    <RotateCw class="size-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- Composer -->
        <form
          class="px-3 py-2 bg-background/80 backdrop-blur"
          @submit.prevent="onSubmit"
        >
          <div class="flex items-end gap-1 px-1 py-1">
            <button
              type="button"
              class="text-muted-foreground hover:text-foreground p-1 transition"
              aria-label="Conversation menu"
              tabindex="-1"
              disabled
            >
              <Menu class="size-4" />
            </button>
            <textarea
              v-model="composer"
              rows="1"
              placeholder="Type something…"
              autocomplete="off"
              class="flex-1 resize-none bg-transparent text-sm py-1 outline-none placeholder:text-muted-foreground/70 max-h-32"
              @keydown.enter.exact.prevent="onSubmit"
              @input="autoresize"
              ref="textareaEl"
            />
            <button
              type="button"
              class="text-muted-foreground hover:text-foreground p-1 transition"
              aria-label="Voice (coming soon)"
              tabindex="-1"
              disabled
            >
              <Mic class="size-4" />
            </button>
            <button
              type="submit"
              :disabled="!composer.trim() || chat.streaming"
              class="text-primary hover:text-primary/80 disabled:text-muted-foreground/40 p-1 transition"
              aria-label="Send"
            >
              <Loader2 v-if="chat.streaming" class="size-4 animate-spin" />
              <SendHorizontal v-else class="size-4" />
            </button>
          </div>
        </form>
      </aside>
    </Transition>
  </Teleport>
</template>

<script lang="ts" setup>
import { useMediaQuery } from "@vueuse/core";
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  History,
  Loader2,
  Menu,
  Mic,
  Plus,
  RotateCw,
  SendHorizontal,
  ThumbsDown,
  ThumbsUp,
  Trash2,
  X,
} from "lucide-vue-next";
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";

import AiMark from "@/components/AiMark.vue";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { labelForTool } from "@/lib/genai";
import { useAuthStore } from "@/stores/auth";
import { CHAT_MODELS, useChatStore } from "@/stores/chat";

const chat = useChatStore();
const auth = useAuthStore();

const isDesktop = useMediaQuery("(min-width: 640px)");

const composer = ref("");
const scrollEl = ref<HTMLDivElement | null>(null);
const textareaEl = ref<HTMLTextAreaElement | null>(null);

const panelStyle = computed(() => ({
  width: isDesktop.value ? `${chat.panelWidth}px` : undefined,
}));

const roleScopeLabel = computed(() => {
  switch (auth.role) {
    case "admin":
      return "users, professionals, services, and metrics";
    case "professional":
      return "your inbox, scheduled jobs, and earnings";
    case "user":
      return "services, professionals, and your bookings";
    default:
      return "the marketplace";
  }
});

const suggestedPrompts = computed(() => {
  switch (auth.role) {
    case "admin":
      return ["How are we doing this month?", "Show pending approvals", "Top services"];
    case "professional":
      return ["What's in my inbox?", "Weekly recap", "Accept #1"];
    case "user":
      return ["Find me a plumber", "Status of my requests", "I need urgent cleaning"];
    default:
      return ["What can you do?"];
  }
});

function onSuggested(text: string) {
  composer.value = text;
  void onSubmit();
}

async function onSubmit() {
  const text = composer.value;
  if (!text.trim() || chat.streaming) return;
  composer.value = "";
  if (textareaEl.value) textareaEl.value.style.height = "auto";
  // Fire-and-forget so the textarea stays focused while streaming runs.
  void chat.send(text);
  await nextTick();
  textareaEl.value?.focus();
}

function autoresize(e: Event) {
  const el = e.target as HTMLTextAreaElement;
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 128) + "px";
}

function onRegenerate(messageId: string) {
  const idx = chat.messages.findIndex((m) => m.id === messageId);
  if (idx < 1) return;
  const prevUser = chat.messages[idx - 1];
  if (!prevUser || prevUser.role !== "user") return;
  // Drop the assistant message (and any orphans after it) then re-send.
  chat.messages.splice(idx);
  void chat.send(prevUser.text);
}

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function formatRelative(ts: number): string {
  const diffSec = (Date.now() - ts) / 1000;
  if (diffSec < 60) return "Just now";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86_400) return `${Math.floor(diffSec / 3600)}h ago`;
  const d = new Date(ts);
  const today = new Date();
  const yest = new Date(today);
  yest.setDate(yest.getDate() - 1);
  if (d.toDateString() === yest.toDateString()) return "Yesterday";
  if (diffSec < 7 * 86_400) {
    return d.toLocaleDateString([], { weekday: "short" });
  }
  return d.toLocaleDateString([], { month: "short", day: "numeric" });
}

function onLoadConversation(id: string) {
  chat.loadConversation(id);
}

function resultSummary(result: unknown): string {
  if (Array.isArray(result)) {
    return `${result.length} result${result.length === 1 ? "" : "s"}`;
  }
  if (result && typeof result === "object" && "id" in result) {
    return "done";
  }
  return "";
}

function formatResult(result: unknown, status: "running" | "ok" | "error"): string {
  if (status === "running") return "Running…";
  if (status === "error") return String(result ?? "Tool failed");
  if (Array.isArray(result)) {
    return `${result.length} item(s):\n` + JSON.stringify(result.slice(0, 5), null, 2);
  }
  return JSON.stringify(result, null, 2);
}

function renderMarkdownish(text: string): string {
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return escaped
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*(?!\s)([^*]+?)\*/g, "$1<em>$2</em>")
    .replace(/`([^`]+)`/g, "<code class='text-[11px] bg-muted px-1 font-mono'>$1</code>")
    .replace(/\n/g, "<br />");
}

// ─── Left-edge resize ───
const resizing = ref(false);
let startX = 0;
let startWidth = 0;

function onResizeStart(e: MouseEvent) {
  resizing.value = true;
  startX = e.clientX;
  startWidth = chat.panelWidth;
  window.addEventListener("mousemove", onResizeMove);
  window.addEventListener("mouseup", onResizeEnd, { once: true });
  document.body.style.userSelect = "none";
  document.body.style.cursor = "ew-resize";
  e.preventDefault();
}
function onResizeMove(e: MouseEvent) {
  if (!resizing.value) return;
  // Panel is right-docked: dragging left grows it.
  const next = startWidth + (startX - e.clientX);
  chat.setPanelWidth(next);
}
function onResizeEnd() {
  resizing.value = false;
  window.removeEventListener("mousemove", onResizeMove);
  document.body.style.userSelect = "";
  document.body.style.cursor = "";
}
onBeforeUnmount(() => {
  window.removeEventListener("mousemove", onResizeMove);
});

// ─── Autoscroll ───
watch(
  () => chat.messages.flatMap((m) => [m.text, m.toolCalls.length, m.pending ? 1 : 0]),
  async () => {
    await nextTick();
    if (scrollEl.value) {
      scrollEl.value.scrollTop = scrollEl.value.scrollHeight;
    }
  },
  { deep: true },
);

</script>

<style scoped>
/* Bottom fade mask on the message scroller — content dissolves into composer. */
.scroll-fade {
  mask-image: linear-gradient(180deg, black 0%, black 92%, transparent 100%);
  -webkit-mask-image: linear-gradient(180deg, black 0%, black 92%, transparent 100%);
}
</style>
