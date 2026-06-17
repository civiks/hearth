<template>
  <component
    :is="interactive ? 'button' : 'div'"
    :type="interactive ? 'button' : undefined"
    :class="cn(
      'flex w-full items-center gap-4 px-4 py-3.5 text-left',
      interactive && 'press transition-colors hover:bg-muted/50',
      danger && 'text-destructive',
    )"
    @click="interactive && emit('click')"
  >
    <component
      :is="icon"
      class="size-5 shrink-0"
      :class="danger ? 'text-destructive' : 'text-muted-foreground'"
      weight="bold"
    />
    <div class="min-w-0 flex-1">
      <p class="text-sm font-semibold tracking-tight">{{ label }}</p>
      <p v-if="description" class="mt-0.5 text-xs leading-snug text-muted-foreground">
        {{ description }}
      </p>
    </div>
    <span
      v-if="$slots.value || value != null"
      class="max-w-[45%] shrink-0 truncate text-right text-sm text-muted-foreground tabular-nums"
    >
      <slot name="value">{{ value }}</slot>
    </span>
    <PhCaretRight
      v-if="interactive"
      class="size-4 shrink-0 text-muted-foreground/40"
      weight="bold"
    />
  </component>
</template>

<script lang="ts" setup>
import { PhCaretRight } from "@phosphor-icons/vue";
import type { Component } from "vue";
import { cn } from "@/lib/utils";

defineProps<{
  icon: Component;
  label: string;
  description?: string;
  value?: string | number | null;
  interactive?: boolean;
  danger?: boolean;
}>();

const emit = defineEmits<{ click: [] }>();
</script>
