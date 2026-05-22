<template>
  <span class="inline-flex items-center gap-1.5 text-xs capitalize whitespace-nowrap">
    <span
      class="inline-block size-2 rounded-full shrink-0"
      :class="dotClass"
      aria-hidden="true"
    />
    <slot>{{ (label ?? status).replace('_', ' ') }}</slot>
  </span>
</template>

<script lang="ts" setup>
import { computed } from "vue";

const props = defineProps<{
  status: string;
  label?: string | null;
}>();

const STATUS_TO_DOT: Record<string, string> = {
  approved: "bg-success",
  completed: "bg-success",
  active: "bg-success",
  accepted: "bg-info",
  in_progress: "bg-info",
  pending: "bg-warning",
  requested: "bg-warning",
  cancelled: "bg-destructive",
  rejected: "bg-destructive",
  blocked: "bg-destructive",
};

const dotClass = computed(
  () => STATUS_TO_DOT[props.status] ?? "bg-muted-foreground/50",
);
</script>
