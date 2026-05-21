<template>
  <span class="inline-flex items-center gap-0.5" :class="$attrs.class">
    <Star
      v-for="i in 5"
      :key="i"
      class="size-3.5"
      :class="i <= rounded ? 'fill-amber-400 text-amber-400' : 'text-muted-foreground/30'"
    />
  </span>
</template>

<script lang="ts" setup>
import { Star } from "lucide-vue-next";
import { computed } from "vue";

const props = defineProps<{ rating: number }>();
const rounded = computed(() => Math.round(props.rating));
</script>
