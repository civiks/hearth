<template>
  <span
    :class="[
      'inline-flex items-center px-2 py-0.5 text-xs font-medium capitalize whitespace-nowrap',
      tagClass,
    ]"
  >
    <slot>{{ (label ?? status).replace('_', ' ') }}</slot>
  </span>
</template>

<script lang="ts" setup>
import { computed } from "vue";

const props = defineProps<{
  status: string;
  label?: string | null;
}>();

// Carbon "Tag" component: each status pairs a background tint with a text
// tint so the chip is readable on any cell background.
const STATUS_TO_TAG: Record<string, string> = {
  // Green — terminal-positive
  approved: "bg-emerald-100 text-emerald-800",
  completed: "bg-emerald-100 text-emerald-800",
  active: "bg-emerald-100 text-emerald-800",
  // Blue — in-flight, neutral-positive
  accepted: "bg-blue-100 text-blue-800",
  in_progress: "bg-blue-100 text-blue-800",
  // Amber — needs-attention
  pending: "bg-amber-100 text-amber-800",
  requested: "bg-amber-100 text-amber-800",
  // Red — terminated / blocked
  cancelled: "bg-red-100 text-red-800",
  rejected: "bg-red-100 text-red-800",
  blocked: "bg-red-100 text-red-800",
};

const tagClass = computed(
  () => STATUS_TO_TAG[props.status] ?? "bg-muted text-muted-foreground",
);
</script>
