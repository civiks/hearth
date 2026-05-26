<template>
  <img
    :src="finalSrc"
    :alt="name"
    loading="lazy"
    class="rounded-full bg-muted object-cover"
    :class="$attrs.class"
  />
</template>

<script lang="ts" setup>
import { computed } from "vue";

const props = defineProps<{ name: string; src?: string | null }>();

const finalSrc = computed(
  () =>
    props.src ||
    `https://api.dicebear.com/9.x/notionists/svg?seed=${encodeURIComponent(props.name)}`,
);
</script>
