<template>
  <DashboardWidget
    :class="['ai-surface ai-outline', $attrs.class as HTMLAttributes['class']]"
    title="Weekly digest"
    subtitle="Auto-generated from the latest analytics"
    body-class="text-sm space-y-2"
  >
    <template #title>
      <span class="inline-flex items-center gap-2">
        <AiMark class="size-3.5" />
        Weekly digest
      </span>
    </template>
    <template #action>
      <div class="flex items-center gap-4">
        <button
          v-show="!collapsed"
          type="button"
          class="text-xs text-primary inline-flex items-center gap-1.5 hover:underline underline-offset-4 disabled:opacity-50"
          :disabled="streaming"
          @click="regenerate"
        >
          {{ streaming ? "Generating…" : "Regenerate" }}
        </button>
        <button
          type="button"
          class="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors"
          :aria-label="collapsed ? 'Expand digest' : 'Collapse digest'"
          @click="collapsed = !collapsed"
        >
          <span v-if="collapsed" class="text-xs tracking-tight">Show</span>
          <ChevronUp v-if="!collapsed" class="size-3.5" />
          <ChevronDown v-else class="size-3.5" />
        </button>
      </div>
    </template>

    <div v-show="!collapsed">
      <div v-if="!narrative && !streaming" class="text-xs text-muted-foreground">
        Waiting for analytics…
      </div>
      <div
        v-else
        class="leading-relaxed"
        v-html="renderMarkdownish(narrative)"
      />
      <span
        v-if="streaming"
        class="inline-block size-2 bg-muted-foreground/60 align-middle animate-pulse"
        aria-hidden="true"
      />
    </div>
  </DashboardWidget>
</template>

<script lang="ts" setup>
import { computed, type HTMLAttributes, ref, watch } from "vue";
import { useLocalStorage } from "@vueuse/core";
import { ChevronDown, ChevronUp } from "lucide-vue-next";

import AiMark from "@/components/AiMark.vue";
import { DashboardWidget } from "@/components/dashboard";
import { streamScript, tokenize, type AgentEvent } from "@/lib/genai";

const collapsed = useLocalStorage("hs.digest.ops.collapsed", true);

interface TrendPoint { date: string; count: number }
interface StatusSlice { status: string; count: number }
interface ServicePoint { name: string; count: number }
interface Analytics {
  request_trends?: TrendPoint[];
  service_popularity?: ServicePoint[];
  user_registrations?: TrendPoint[];
  professional_status?: StatusSlice[];
  user_status?: StatusSlice[];
}

const props = defineProps<{
  analytics: Analytics | null;
  loaded?: boolean;
}>();

defineOptions({ inheritAttrs: false });

const narrative = ref("");
const streaming = ref(false);

const facts = computed(() => {
  const a = props.analytics ?? {};
  const trends = a.request_trends ?? [];
  const total = trends.reduce((s, p) => s + p.count, 0);
  const mid = Math.floor(trends.length / 2);
  const earlier = trends.slice(0, mid).reduce((s, p) => s + p.count, 0);
  const latest = trends.slice(mid).reduce((s, p) => s + p.count, 0);
  const deltaPct =
    earlier > 0 ? Math.round(((latest - earlier) / earlier) * 100) : null;

  const topService = (a.service_popularity ?? [])[0];
  const proPending =
    (a.professional_status ?? []).find((s) => s.status === "pending")?.count ?? 0;
  const userBlocked =
    (a.user_status ?? []).find((s) => s.status === "blocked")?.count ?? 0;
  return { total, deltaPct, topService, proPending, userBlocked };
});

function buildLines(): string[] {
  const f = facts.value;
  const lines: string[] = [];
  if (f.deltaPct === null) {
    lines.push(`Tracking **${f.total}** lifetime requests so far.`);
  } else if (f.deltaPct > 5) {
    lines.push(
      `Bookings up **${f.deltaPct}%** vs the prior period — **${f.total}** lifetime requests.`,
    );
  } else if (f.deltaPct < -5) {
    lines.push(
      `Bookings down **${Math.abs(f.deltaPct)}%** — worth checking what cooled off.`,
    );
  } else {
    lines.push(`Bookings holding steady — **${f.total}** lifetime requests.`);
  }
  if (f.topService) {
    lines.push(
      `**${f.topService.name}** is the top category with ${f.topService.count} bookings.`,
    );
  }
  if (f.proPending > 0) {
    lines.push(
      `**${f.proPending}** professional${f.proPending === 1 ? "" : "s"} awaiting approval — review on the Professionals tab.`,
    );
  } else {
    lines.push(`No pending professional approvals.`);
  }
  if (f.userBlocked > 0) {
    lines.push(`Heads up: **${f.userBlocked}** blocked user account(s).`);
  }
  return lines;
}

/** Instant render — used on mount once analytics arrives. */
function generate() {
  if (!props.loaded || !props.analytics) return;
  narrative.value = buildLines().join("\n");
}

/** Streaming render — used on user-initiated regenerate. */
async function regenerate() {
  if (streaming.value || !props.loaded || !props.analytics) return;
  streaming.value = true;
  narrative.value = "";
  const script: AgentEvent[] = [];
  buildLines().forEach((line, i) => {
    if (i > 0) script.push({ type: "text", delta: "\n" });
    script.push(...tokenize(line));
  });
  const reader = streamScript(script).getReader();
  try {
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      if (value.type === "text") narrative.value += value.delta;
    }
  } finally {
    streaming.value = false;
  }
}

// Wait for the parent to finish loading before rendering — otherwise the
// initial empty `{}` analytics produces a flash of "0 lifetime requests"
// that gets replaced once the real payload arrives.
watch(
  () => [props.loaded, props.analytics?.request_trends?.length ?? 0] as const,
  ([loaded]) => {
    if (loaded) generate();
  },
  { immediate: true },
);

function renderMarkdownish(text: string): string {
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return escaped
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br />");
}
</script>
