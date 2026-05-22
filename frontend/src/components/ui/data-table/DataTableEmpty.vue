<template>
  <div
    class="bg-card p-12 text-center text-sm text-muted-foreground"
    role="status"
  >
    <slot>{{ message }}</slot>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ message?: string }>();
</script>
