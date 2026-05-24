<template>
  <!--
    Two render modes:
      • inline  — child of a SplitterPanel on desktop. Fills its parent, no
                  Teleport, no transition.
      • overlay — Teleported to body on mobile (<640px). Backdrop + slide-in
                  from the right.
  -->
  <Teleport to="body" :disabled="mode === 'inline'">
    <Transition
      enter-active-class="transition-opacity duration-150"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="mode === 'overlay' && chat.open"
        class="fixed inset-0 z-40 bg-black/40"
        aria-hidden="true"
        @click="chat.close()"
      />
    </Transition>

    <Transition
      :enter-active-class="mode === 'overlay' ? 'transition-transform duration-200 ease-out' : ''"
      :leave-active-class="mode === 'overlay' ? 'transition-transform duration-150 ease-in' : ''"
      :enter-from-class="mode === 'overlay' ? 'translate-x-full' : ''"
      :leave-to-class="mode === 'overlay' ? 'translate-x-full' : ''"
    >
      <aside
        v-if="visible"
        :class="[
          'flex flex-col bg-background ai-surface ai-outline',
          mode === 'overlay'
            ? 'fixed inset-0 z-50 shadow-2xl'
            : 'h-full',
        ]"
        :role="mode === 'overlay' ? 'dialog' : 'complementary'"
        aria-label="Assistant"
      >
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
                <Button
                  variant="ghost"
                  size="icon"
                  class="size-8"
                  aria-label="Conversation history"
                >
                  <History class="size-4" />
                </Button>
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
        <!--
          pb-16 reserves a safe area at the bottom so the last message sits
          above the (pixel-fixed) fade mask rather than streaming/landing
          inside it.
        -->
        <div
          ref="scrollEl"
          class="flex-1 overflow-y-auto px-4 pt-4 pb-16 space-y-5 scroll-fade"
          role="log"
          aria-label="Conversation"
          aria-live="polite"
        >
          <!-- Empty state -->
          <div v-if="!chat.hasMessages" class="space-y-5 pt-2">
            <AiMark class="size-9" />
            <div class="space-y-2">
              <p class="text-base font-medium">Hi {{ firstName }},</p>
              <p class="text-sm text-muted-foreground leading-relaxed">
                I'm hearth AI. {{ roleIntro }} Ask me anything below.
              </p>
            </div>


            <div class="space-y-3">
              <p class="text-sm text-muted-foreground">Or try one of these</p>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="p in suggestedPrompts"
                  :key="p"
                  type="button"
                  class="text-left text-sm border border-primary/30 text-primary hover:bg-primary/5 px-3 py-2 rounded-full transition truncate"
                  @click="onSuggested(p)"
                >
                  {{ p }}
                </button>
              </div>
            </div>

            <p v-if="!DEMO" class="text-[11px] text-muted-foreground pt-2">
              API key isn't configured.
              <RouterLink to="/settings" class="text-primary hover:underline">
                Settings → AI</RouterLink>.
            </p>
          </div>

          <!-- Messages -->
          <template v-for="m in chat.messages" :key="m.id">
            <!-- User turn — byline above, right-aligned grey bubble below -->
            <div v-if="m.role === 'user'" class="space-y-1.5">
              <div class="flex items-center justify-end gap-2 text-[11px]">
                <span class="font-medium">You</span>
                <span class="text-muted-foreground">{{ formatTime(m.timestamp) }}</span>
              </div>
              <div class="flex justify-end">
                <div class="text-sm bg-secondary text-secondary-foreground px-3 py-2 rounded-lg rounded-tr-sm max-w-[85%] whitespace-pre-wrap break-words">
                  {{ m.text }}
                </div>
              </div>
            </div>

            <!-- Assistant turn — avatar + name + time + live state -->
            <div v-else class="space-y-1.5">
              <div class="flex items-center gap-2 text-[11px]">
                <AiMark class="size-5" />
                <span class="font-medium">hearth AI</span>
                <span class="text-muted-foreground">{{ formatTime(m.timestamp) }}</span>
                <span
                  v-if="m.state"
                  class="ml-auto inline-flex items-center gap-1.5 text-muted-foreground"
                >
                  <Loader2 class="size-3 animate-spin" />
                  {{ m.state }}…
                </span>
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
                  v-if="m.text"
                  class="text-sm leading-relaxed"
                  v-html="renderMarkdownish(m.text)"
                />

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

    <!-- AiKeyDialog teleports to body via reka's Dialog primitive, so its
         position here only affects mount lifetime. -->
    <AiKeyDialog v-model:open="keyDialogOpen" />
  </Teleport>
</template>

<script lang="ts" setup>
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
import { computed, nextTick, ref, watch } from "vue";
import { RouterLink } from "vue-router";

import AiKeyDialog from "@/components/AiKeyDialog.vue";
import AiMark from "@/components/AiMark.vue";
import { Button } from "@/components/ui/button";
import { DEMO } from "@/lib/demo/flag";
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

// Auto-opens when chat.needsKeySetup flips true (backend 503'd because no
// Gemini key was configured). Reset to false once the dialog is shown so
// the next failure re-opens it.
const keyDialogOpen = ref(false);

const props = withDefaults(
  defineProps<{ mode?: "inline" | "overlay" }>(),
  { mode: "overlay" },
);

const chat = useChatStore();
const auth = useAuthStore();

// Auto-pop the key dialog when the backend signals it needs one.
watch(
  () => chat.needsKeySetup,
  (v) => {
    if (v) {
      keyDialogOpen.value = true;
      chat.needsKeySetup = false; // one-shot — clear so future 503s re-open
    }
  },
);

const composer = ref("");
const scrollEl = ref<HTMLDivElement | null>(null);
const textareaEl = ref<HTMLTextAreaElement | null>(null);

// Inline mode is gated by parent mount (it only mounts when chat.open is
// true). Overlay mode toggles via chat.open + transition.
const visible = computed(() => props.mode === "inline" || chat.open);

const firstName = computed(() => auth.full_name?.split(" ")[0] || "there");

const roleIntro = computed(() => {
  switch (auth.role) {
    case "admin":
      return "I can summarise platform metrics, walk through pending approvals, and surface trends across categories.";
    case "professional":
      return "I can check incoming requests in your area, help you accept jobs, and recap your weekly activity.";
    case "user":
      return "I can help you find services, book new ones from a description, and track the status of your requests.";
    default:
      return "I can help you explore the marketplace.";
  }
});

const suggestedPrompts = computed(() => {
  switch (auth.role) {
    case "admin":
      return [
        "How are we doing?",
        "Show pending approvals",
        "Top categories",
        "Any flagged users?",
      ];
    case "professional":
      return [
        "What's in my inbox?",
        "Weekly recap",
        "Accept the oldest one",
        "How are my earnings?",
      ];
    case "user":
      return [
        "Find me a plumber",
        "Status of my requests",
        "I need urgent cleaning",
        "Recommend a top-rated pro",
      ];
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
/*
 * Bottom fade mask on the message scroller — content dissolves into the
 * composer. Fixed at 48px so the pb-16 (64px) bottom padding always leaves
 * ~16px of unmasked clearance regardless of viewport height.
 */
.scroll-fade {
  mask-image: linear-gradient(180deg, black, black calc(100% - 48px), transparent);
  -webkit-mask-image: linear-gradient(180deg, black, black calc(100% - 48px), transparent);
}
</style>
