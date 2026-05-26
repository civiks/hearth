<template>
  <div v-if="cancelled" class="flex items-center gap-2 text-xs text-destructive">
    <Ban class="size-3.5" />
    <span class="font-medium">Cancelled</span>
  </div>
  <div v-else class="space-y-2">
    <ol class="flex items-center">
      <template v-for="(step, i) in steps" :key="step.key">
        <li
          class="inline-flex size-6 shrink-0 items-center justify-center rounded-full text-[10px] font-medium"
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
        </li>
        <div
          v-if="i < steps.length - 1"
          class="flex-1 h-px mx-1"
          :class="i < currentIndex ? 'bg-primary' : 'bg-muted'"
        />
      </template>
    </ol>
    <p class="text-xs text-muted-foreground">
      Step {{ currentIndex + 1 }} of {{ steps.length }}
      <span class="font-medium text-foreground">· {{ steps[currentIndex]!.label }}</span>
    </p>
  </div>
</template>

<script lang="ts" setup>
import { Ban, CalendarCheck, CheckCheck, Hourglass, Wrench } from "lucide-vue-next";
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
