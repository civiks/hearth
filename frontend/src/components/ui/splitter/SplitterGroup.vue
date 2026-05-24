<script setup lang="ts">
import { SplitterGroup, type SplitterGroupProps } from "reka-ui";

defineProps<SplitterGroupProps>();
defineEmits<{ layout: [sizes: number[]] }>();
</script>

<template>
  <SplitterGroup v-bind="$props" @layout="$emit('layout', $event)">
    <slot />
  </SplitterGroup>
</template>
