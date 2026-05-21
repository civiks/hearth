<template>
  <div class="flex flex-col gap-1">
    <span class="text-xs font-medium uppercase tracking-wide text-muted-foreground">
      {{ label }}
    </span>
    <span class="text-sm text-foreground">
      <slot>{{ value }}</slot>
    </span>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ label: string; value?: string | number | null }>();
</script>
