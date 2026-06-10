<template>
  <DashboardWidget
    :class="['ai-surface ai-outline', $attrs.class as HTMLAttributes['class']]"
    title="Weekly digest"
    subtitle="Auto-generated from your activity"
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
          <PhCaretUp v-if="!collapsed" class="size-3.5" />
          <PhCaretDown v-else class="size-3.5" />
        </button>
      </div>
    </template>

    <div v-show="!collapsed">
      <div v-if="!narrative && !streaming" class="text-xs text-muted-foreground">
        No data yet.
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
import {
  PhCaretDown,
  PhCaretUp,
} from '@phosphor-icons/vue';

import AiMark from "@/components/AiMark.vue";
import { DashboardWidget } from "@/components/dashboard";
import { streamScript, tokenize, type AgentEvent } from "@/lib/genai";

const collapsed = useLocalStorage("hs.digest.pro.collapsed", true);

interface ProRequestStat {
  id: number;
  service_id: number;
  service_status: string;
  date_of_request?: string;
}
interface ServiceLite {
  id: number;
  base_price: number;
}

const props = defineProps<{
  requests: ProRequestStat[];
  services: ServiceLite[];
  loaded?: boolean;
}>();

defineOptions({ inheritAttrs: false });

const narrative = ref("");
const streaming = ref(false);

const facts = computed(() => {
  const reqs = props.requests ?? [];
  const services = props.services ?? [];

  const completed = reqs.filter((r) => r.service_status === "completed");
  const inFlight = reqs.filter(
    (r) => r.service_status === "in_progress" || r.service_status === "accepted",
  );
  const pending = reqs.filter((r) => r.service_status === "requested");

  const earnings = completed.reduce((sum, r) => {
    const s = services.find((x) => x.id === r.service_id);
    return sum + (s?.base_price ?? 0);
  }, 0);

  // Trend: completed in the last 30 days vs the 30 before that.
  const now = Date.now();
  const day = 86_400_000;
  const recentCompleted = completed.filter((r) => {
    if (!r.date_of_request) return false;
    return now - new Date(r.date_of_request).getTime() <= 30 * day;
  }).length;
  const priorCompleted = completed.filter((r) => {
    if (!r.date_of_request) return false;
    const age = now - new Date(r.date_of_request).getTime();
    return age > 30 * day && age <= 60 * day;
  }).length;
  const deltaPct =
    priorCompleted > 0
      ? Math.round(((recentCompleted - priorCompleted) / priorCompleted) * 100)
      : null;

  const oldestPending = pending
    .slice()
    .sort((a, b) => (a.date_of_request ?? "").localeCompare(b.date_of_request ?? ""))[0];

  return {
    completedCount: completed.length,
    inFlightCount: inFlight.length,
    pendingCount: pending.length,
    earnings,
    recentCompleted,
    deltaPct,
    oldestPendingId: oldestPending?.id ?? null,
  };
});

function formatEarnings(v: number): string {
  if (v >= 100_000) return `₹${(v / 100_000).toFixed(1)}L`;
  if (v >= 1_000) return `₹${(v / 1_000).toFixed(1)}k`;
  return `₹${v}`;
}

function buildLines(): string[] {
  const f = facts.value;
  const lines: string[] = [];

  if (f.completedCount === 0 && f.inFlightCount === 0 && f.pendingCount === 0) {
    lines.push(
      `You're all set up — once requests start coming in for your category, I'll summarise your week here every time you visit.`,
    );
    return lines;
  }

  lines.push(
    `**${f.completedCount}** completed job${f.completedCount === 1 ? "" : "s"} to date, earning roughly **${formatEarnings(f.earnings)}** at your current rate.`,
  );

  if (f.deltaPct !== null) {
    if (f.deltaPct > 10) {
      lines.push(
        `You completed **${f.recentCompleted}** job${f.recentCompleted === 1 ? "" : "s"} in the last 30 days — that's **${f.deltaPct}% more** than the prior month. Keep the momentum.`,
      );
    } else if (f.deltaPct < -10) {
      lines.push(
        `Completed work dipped **${Math.abs(f.deltaPct)}%** vs the prior month (${f.recentCompleted} this month vs ${f.recentCompleted + Math.abs(f.deltaPct)} before). Worth claiming pending jobs faster.`,
      );
    } else {
      lines.push(
        `PhActivity is steady — **${f.recentCompleted}** completed in the last 30 days, in line with the prior month.`,
      );
    }
  } else if (f.recentCompleted > 0) {
    lines.push(`**${f.recentCompleted}** of those were in the last 30 days.`);
  }

  if (f.pendingCount > 0) {
    lines.push(
      `**${f.pendingCount}** request${f.pendingCount === 1 ? "" : "s"} sitting in your inbox right now${f.oldestPendingId ? ` — oldest is **#${f.oldestPendingId}**` : ""}. Customers respond best within the first 30 minutes.`,
    );
  } else {
    lines.push(
      `Inbox is clear. Most pros use this window to follow up on completed jobs for reviews — your rating drives the next round of bookings.`,
    );
  }

  if (f.inFlightCount > 0) {
    lines.push(
      `**${f.inFlightCount}** job${f.inFlightCount === 1 ? "" : "s"} still in flight — mark them **Completed** from the Requests tab as soon as you wrap on-site so the customer can leave a review.`,
    );
  }
  return lines;
}

/** Instant render — used on mount once data arrives. */
function generate() {
  if (!props.loaded || !props.requests) return;
  narrative.value = buildLines().join("\n\n");
}

/** Streaming render — used on user-initiated regenerate. */
async function regenerate() {
  if (streaming.value || !props.loaded || !props.requests) return;
  streaming.value = true;
  narrative.value = "";
  const script: AgentEvent[] = [];
  buildLines().forEach((line, i) => {
    if (i > 0) script.push({ type: "text", delta: "\n\n" });
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
// initial empty `[]` requests array produces a flash of the "all set up"
// empty-state copy that gets replaced once the real payload arrives.
watch(
  () => [props.loaded, props.requests?.length ?? 0] as const,
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
