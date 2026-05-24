<template>
  <div class="flex items-center justify-between gap-6 py-4 border-b last:border-b-0">
    <div class="min-w-0">
      <p class="text-sm font-medium">{{ label }}</p>
      <p
        v-if="$slots.hint || hint"
        class="text-xs text-muted-foreground mt-0.5"
      >
        <slot name="hint">{{ hint }}</slot>
      </p>
    </div>
    <div class="shrink-0">
      <slot />
    </div>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ label: string; hint?: string }>();
</script>
