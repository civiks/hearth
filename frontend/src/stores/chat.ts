import { defineStore } from "pinia";

import { runAgent, toolsForRole, type AgentEvent } from "@/lib/genai";
import { useAuthStore } from "@/stores/auth";

export interface ChatToolCall {
  id: string;
  name: string;
  args: Record<string, unknown>;
  status: "running" | "ok" | "error";
  result?: unknown;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  toolCalls: ChatToolCall[];
  pending?: boolean;
  timestamp: number;
  feedback?: "up" | "down";
  /**
   * Current agent activity verb ("Thinking", "Searching", "Writing", …).
   * Set by `state` events from the agent stream; cleared once text starts
   * arriving or on completion.
   */
  state?: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
  updatedAt: number;
}

export interface ChatModel {
  id: string;
  name: string;
  provider: string;
  /** Hex color used as the model "brand dot" in the picker. */
  color: string;
  tagline: string;
}

export const CHAT_MODELS: ChatModel[] = [
  {
    id: "claude-opus-4-7",
    name: "Claude Opus 4.7",
    provider: "Anthropic",
    color: "#D97757",
    tagline: "Most capable",
  },
  {
    id: "claude-sonnet-4-6",
    name: "Claude Sonnet 4.6",
    provider: "Anthropic",
    color: "#E8A66E",
    tagline: "Fast & balanced",
  },
  {
    id: "gpt-5",
    name: "GPT-5",
    provider: "OpenAI",
    color: "#10A37F",
    tagline: "OpenAI flagship",
  },
  {
    id: "gemini-2.5-pro",
    name: "Gemini 2.5 Pro",
    provider: "Google",
    color: "#1A73E8",
    tagline: "Long context",
  },
];

interface State {
  open: boolean;
  streaming: boolean;
  messages: ChatMessage[];
  modelId: string;
  conversations: Conversation[];
  currentConversationId: string | null;
}

const MODEL_KEY = "hearth.chat.modelId";
const HISTORY_KEY_PREFIX = "hearth.chat.history.";

/** Reka splitter `autoSaveId` — handles its own % layout persistence. */
export const CHAT_SPLITTER_ID = "hearth.chat.splitter";
/** Default chat panel size as a percentage of the splitter group width. */
export const CHAT_DEFAULT_SIZE = 28;
/** Lower bound — anything smaller would clip the composer. */
export const CHAT_MIN_SIZE = 22;
/** Upper bound — half the screen, per design. */
export const CHAT_MAX_SIZE = 50;

function historyKeyFor(userId: number | null): string | null {
  return userId == null ? null : `${HISTORY_KEY_PREFIX}${userId}`;
}

function readHistory(userId: number | null): Conversation[] {
  const key = historyKeyFor(userId);
  if (!key || typeof window === "undefined") return [];
  const raw = window.localStorage.getItem(key);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeHistory(userId: number | null, convs: Conversation[]): void {
  const key = historyKeyFor(userId);
  if (!key || typeof window === "undefined") return;
  window.localStorage.setItem(key, JSON.stringify(convs));
}

function deriveTitle(messages: ChatMessage[]): string {
  const firstUser = messages.find((m) => m.role === "user");
  if (!firstUser) return "New conversation";
  const text = firstUser.text.trim().replace(/\s+/g, " ");
  return text.length > 60 ? text.slice(0, 57) + "…" : text;
}

let convSeq = 0;
function nextConvId(): string {
  return `c_${++convSeq}_${Date.now().toString(36)}`;
}

function readModelId(): string {
  if (typeof window === "undefined") return CHAT_MODELS[0].id;
  const raw = window.localStorage.getItem(MODEL_KEY);
  if (raw && CHAT_MODELS.some((m) => m.id === raw)) return raw;
  return CHAT_MODELS[0].id;
}

let msgSeq = 0;
function nextId(): string {
  return `m_${++msgSeq}_${Date.now().toString(36)}`;
}

export const useChatStore = defineStore("chat", {
  state: (): State => ({
    open: false,
    streaming: false,
    messages: [],
    modelId: readModelId(),
    conversations: [],
    currentConversationId: null,
  }),
  getters: {
    availableTools: () => {
      const auth = useAuthStore();
      return toolsForRole(auth.role).map((t) => ({ name: t.name, description: t.description }));
    },
    hasMessages: (s) => s.messages.length > 0,
    currentModel: (s): ChatModel =>
      CHAT_MODELS.find((m) => m.id === s.modelId) ?? CHAT_MODELS[0],
    /** Past conversations sorted by most recent update. */
    sortedConversations: (s): Conversation[] =>
      [...s.conversations].sort((a, b) => b.updatedAt - a.updatedAt),
  },
  actions: {
    toggle() {
      this.open = !this.open;
    },
    close() {
      this.open = false;
    },
    /** Clear active conversation in memory (used on user change). */
    reset() {
      this.messages = [];
      this.currentConversationId = null;
      this.conversations = [];
    },
    /** Load saved conversations for the current authenticated user. */
    loadUserHistory() {
      const auth = useAuthStore();
      this.conversations = readHistory(auth.user_id);
      this.messages = [];
      this.currentConversationId = null;
    },
    /**
     * Persist the active thread to the user's conversation history. Called
     * after each turn completes and when switching conversations. No-op if
     * the thread is empty.
     */
    persistCurrent() {
      if (this.messages.length === 0) return;
      const auth = useAuthStore();
      const now = Date.now();
      const snapshot: ChatMessage[] = JSON.parse(JSON.stringify(this.messages));
      const title = deriveTitle(this.messages);
      if (this.currentConversationId) {
        const idx = this.conversations.findIndex(
          (c) => c.id === this.currentConversationId,
        );
        if (idx >= 0) {
          this.conversations[idx] = {
            ...this.conversations[idx],
            title,
            messages: snapshot,
            updatedAt: now,
          };
        }
      } else {
        const conv: Conversation = {
          id: nextConvId(),
          title,
          messages: snapshot,
          createdAt: now,
          updatedAt: now,
        };
        this.currentConversationId = conv.id;
        this.conversations = [conv, ...this.conversations];
      }
      writeHistory(auth.user_id, this.conversations);
    },
    /** Save the active thread (if any) and start an empty one. */
    startNew() {
      this.persistCurrent();
      this.messages = [];
      this.currentConversationId = null;
    },
    /** Save the current thread, then load a saved conversation by id. */
    loadConversation(id: string) {
      this.persistCurrent();
      const conv = this.conversations.find((c) => c.id === id);
      if (!conv) return;
      this.messages = JSON.parse(JSON.stringify(conv.messages));
      this.currentConversationId = id;
    },
    deleteConversation(id: string) {
      const auth = useAuthStore();
      this.conversations = this.conversations.filter((c) => c.id !== id);
      if (this.currentConversationId === id) {
        this.messages = [];
        this.currentConversationId = null;
      }
      writeHistory(auth.user_id, this.conversations);
    },
    setModel(id: string) {
      if (!CHAT_MODELS.some((m) => m.id === id)) return;
      this.modelId = id;
      if (typeof window !== "undefined") {
        window.localStorage.setItem(MODEL_KEY, id);
      }
    },
    setFeedback(messageId: string, value: "up" | "down") {
      const msg = this.messages.find((m) => m.id === messageId);
      if (!msg || msg.role !== "assistant") return;
      msg.feedback = msg.feedback === value ? undefined : value;
    },
    async send(text: string) {
      const trimmed = text.trim();
      if (!trimmed || this.streaming) return;

      const auth = useAuthStore();

      const now = Date.now();
      const userMsg: ChatMessage = {
        id: nextId(),
        role: "user",
        text: trimmed,
        toolCalls: [],
        timestamp: now,
      };
      const assistantMsg: ChatMessage = {
        id: nextId(),
        role: "assistant",
        text: "",
        toolCalls: [],
        pending: true,
        timestamp: now,
      };
      this.messages.push(userMsg, assistantMsg);
      this.streaming = true;

      const stream = runAgent(trimmed, auth.role);
      const reader = stream.getReader();
      try {
        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          this.applyEvent(assistantMsg.id, value);
        }
      } finally {
        assistantMsg.pending = false;
        this.streaming = false;
        this.persistCurrent();
      }
    },
    applyEvent(messageId: string, ev: AgentEvent) {
      const msg = this.messages.find((m) => m.id === messageId);
      if (!msg) return;
      switch (ev.type) {
        case "text":
          // First text token clears the state label — once writing begins
          // the visible stream is its own progress indicator.
          if (msg.state) msg.state = undefined;
          msg.text += ev.delta;
          break;
        case "state":
          msg.state = ev.status;
          break;
        case "tool_call":
          msg.toolCalls.push({
            id: ev.id,
            name: ev.name,
            args: ev.args,
            status: "running",
          });
          break;
        case "tool_result": {
          const tc = msg.toolCalls.find((c) => c.id === ev.id);
          if (tc) {
            tc.status = ev.ok ? "ok" : "error";
            tc.result = ev.data;
          }
          break;
        }
        case "done":
          msg.pending = false;
          msg.state = undefined;
          break;
      }
    },
  },
});
