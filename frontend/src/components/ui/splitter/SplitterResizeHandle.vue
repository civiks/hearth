<script setup lang="ts">
import { GripVertical } from "@lucide/vue";
import { SplitterResizeHandle, type SplitterResizeHandleProps } from "reka-ui";
import { computed, type HTMLAttributes } from "vue";

import { cn } from "@/lib/utils";

const props = defineProps<SplitterResizeHandleProps & { class?: HTMLAttributes["class"] }>();

const delegated = computed(() => {
  const { class: _omit, ...rest } = props;
  return rest;
});
</script>

<template>
  <SplitterResizeHandle
    v-bind="delegated"
    :class="cn(
      // Wider hit area than the visible divider so it's forgiving to grab.
      // Native cursor + reka data-state attrs drive color transitions.
      'relative shrink-0 outline-none group/handle flex items-center justify-center w-2',
      'data-[resize-handle-state=hover]:bg-primary/5',
      'focus-visible:outline-none',
      $props.class,
    )"
  >
    <!-- Always-visible 1px divider sitting on the center line. -->
    <div
      class="pointer-events-none absolute inset-y-0 left-1/2 -translate-x-1/2 w-px bg-border transition-colors group-data-[resize-handle-state=hover]/handle:bg-primary/60 group-data-[resize-handle-state=drag]/handle:bg-primary"
    />

    <!-- Knob: small rounded pill with a grip icon so the affordance reads. -->
    <div
      class="relative z-10 flex h-8 w-3 items-center justify-center rounded-sm border bg-background transition-colors group-data-[resize-handle-state=hover]/handle:border-primary group-data-[resize-handle-state=hover]/handle:text-primary group-data-[resize-handle-state=drag]/handle:border-primary group-data-[resize-handle-state=drag]/handle:bg-primary/10 group-data-[resize-handle-state=drag]/handle:text-primary"
    >
      <GripVertical class="size-3 text-muted-foreground transition-colors group-data-[resize-handle-state=hover]/handle:text-primary group-data-[resize-handle-state=drag]/handle:text-primary" />
    </div>

    <slot />
  </SplitterResizeHandle>
</template>
