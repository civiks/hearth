<template>
  <div v-if="cancelled" class="flex items-center gap-2 text-xs text-destructive">
    <Ban class="size-3.5" />
    <span class="font-medium">Cancelled</span>
  </div>
  <ol v-else class="flex items-center gap-1">
    <li
      v-for="(step, i) in steps"
      :key="step.key"
      class="flex items-center gap-1"
    >
      <span
        class="inline-flex size-5 items-center justify-center text-[10px] font-medium"
        :class="[
          i < currentIndex
            ? 'bg-primary text-primary-foreground'
            : i === currentIndex
            ? 'bg-primary/90 text-primary-foreground ring-2 ring-primary/20'
            : 'bg-muted text-muted-foreground',
        ]"
      >
        <component :is="step.icon" v-if="i <= currentIndex" class="size-3" />
        <span v-else>{{ i + 1 }}</span>
      </span>
      <span
        class="text-xs whitespace-nowrap"
        :class="i <= currentIndex ? 'text-foreground font-medium' : 'text-muted-foreground'"
      >
        {{ step.label }}
      </span>
      <ChevronRight
        v-if="i < steps.length - 1"
        class="size-3 text-muted-foreground/50"
      />
    </li>
  </ol>
</template>

<script lang="ts" setup>
import { Ban, CalendarCheck, CheckCheck, ChevronRight, Hourglass, Wrench } from "lucide-vue-next";
import { computed } from "vue";

const props = defineProps<{ status: string }>();

const steps = [
  { key: "requested", label: "Requested", icon: Hourglass },
  { key: "accepted", label: "Accepted", icon: CalendarCheck },
  { key: "in_progress", label: "In progress", icon: Wrench },
  { key: "completed", label: "Completed", icon: CheckCheck },
];

const cancelled = computed(() => props.status === "cancelled");
const currentIndex = computed(() => {
  const idx = steps.findIndex((s) => s.key === props.status);
  return idx < 0 ? 0 : idx;
});
</script>
