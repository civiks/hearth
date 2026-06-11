<template>
  <div v-if="cancelled" class="flex items-center gap-2 text-xs text-destructive">
    <PhProhibit class="size-3.5" weight="bold" />
    <span class="font-medium">Cancelled</span>
  </div>
  <ol v-else>
    <li
      v-for="(step, i) in steps"
      :key="step.key"
      class="relative flex items-start gap-3"
      :class="i < steps.length - 1 ? 'pb-3' : ''"
    >
      <div
        v-if="i < steps.length - 1"
        class="absolute left-[9px] top-5 bottom-0 border-l-2 border-dashed"
        :class="i < currentIndex ? 'border-primary/30' : 'border-muted-foreground/15'"
      />
      <span
        class="relative z-10 inline-flex size-5 shrink-0 items-center justify-center rounded-full"
        :class="[
          i < currentIndex ? 'bg-primary text-primary-foreground' :
          i === currentIndex ? 'bg-primary text-primary-foreground ring-2 ring-primary/20 ring-offset-1' :
          'bg-muted text-muted-foreground'
        ]"
      >
        <component :is="step.icon" v-if="i <= currentIndex" class="size-3" />
      </span>
      <span
        class="text-sm leading-5"
        :class="i === currentIndex ? 'font-medium' : 'text-muted-foreground'"
      >
        {{ step.label }}
      </span>
    </li>
  </ol>
</template>

<script lang="ts" setup>
import {
  PhProhibit,
  PhCalendarCheck,
  PhChecks,
  PhHourglass,
  PhWrench,
} from '@phosphor-icons/vue';
import { computed } from "vue";

const props = defineProps<{ status: string }>();

const steps = [
  { key: "requested", label: "Requested", icon: PhHourglass },
  { key: "accepted", label: "Accepted", icon: PhCalendarCheck },
  { key: "in_progress", label: "In progress", icon: PhWrench },
  { key: "completed", label: "Completed", icon: PhChecks },
];

const cancelled = computed(() => props.status === "cancelled");
const currentIndex = computed(() => {
  const idx = steps.findIndex((s) => s.key === props.status);
  return idx < 0 ? 0 : idx;
});
</script>
