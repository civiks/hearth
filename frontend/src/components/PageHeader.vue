<template>
  <header class="flex items-start justify-between gap-4 mb-4 sm:mb-5">
    <div class="min-w-0">
      <h1 class="text-xl sm:text-2xl font-semibold tracking-tight">{{ title }}</h1>
      <p v-if="description" class="text-sm text-muted-foreground mt-1">{{ description }}</p>
    </div>
    <div v-if="$slots.default" class="shrink-0 flex items-center gap-2">
      <slot />
    </div>
  </header>
</template>

<script lang="ts" setup>
defineProps<{ title: string; description?: string }>();
</script>
