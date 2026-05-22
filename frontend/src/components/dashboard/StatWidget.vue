<script setup lang="ts">
import { ArrowDown, ArrowUp } from "lucide-vue-next";
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import DashboardWidget from "./DashboardWidget.vue";
import Sparkline from "./Sparkline.vue";

const props = defineProps<{
  title: string;
  value: string | number;
  delta?: number;
  trend?: number[];
  to?: RouteLocationRaw;
}>();

const direction = computed<"up" | "down" | null>(() => {
  if (props.delta == null || props.delta === 0) return null;
  return props.delta > 0 ? "up" : "down";
});

const deltaText = computed(() => {
  if (props.delta == null || props.delta === 0) return null;
  const pct = Math.abs(props.delta * 100);
  return `${pct.toFixed(pct >= 10 ? 0 : 1)}%`;
});

const deltaColor = computed(() => {
  if (direction.value === "up") return "text-success";
  if (direction.value === "down") return "text-destructive";
  return "text-muted-foreground";
});

const hasTrend = computed(() => Boolean(props.trend && props.trend.length));
</script>

<template>
  <DashboardWidget :title="title" :view-all-to="to">
    <div class="flex items-center justify-between gap-3">
      <div class="flex items-baseline gap-2 min-w-0">
        <span class="text-3xl font-light leading-none tabular-nums">{{ value }}</span>
        <span
          v-if="deltaText"
          class="inline-flex items-baseline gap-0.5 text-xs font-medium"
          :class="deltaColor"
        >
          <ArrowUp v-if="direction === 'up'" class="size-3 self-center" :stroke-width="2.5" />
          <ArrowDown v-else class="size-3 self-center" :stroke-width="2.5" />
          {{ deltaText }}
        </span>
      </div>
      <div v-if="hasTrend" class="w-20 -mr-1 shrink-0">
        <Sparkline :data="trend!" :height="28" />
      </div>
    </div>
  </DashboardWidget>
</template>
