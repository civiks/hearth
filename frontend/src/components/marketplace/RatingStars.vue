<template>
  <span class="inline-flex items-center gap-0.5" :class="$attrs.class">
    <PhStar
      v-for="i in 5"
      :key="i"
      class="size-3.5"
      :weight="i <= rounded ? 'fill' : 'regular'"
      :class="i <= rounded ? 'text-amber-400' : 'text-muted-foreground/30'"
    />
  </span>
</template>

<script lang="ts" setup>
import {
  PhStar,
} from '@phosphor-icons/vue';
import { computed } from "vue";

const props = defineProps<{ rating: number }>();
const rounded = computed(() => Math.round(props.rating));
</script>
