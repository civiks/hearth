<script setup lang="ts" generic="T">
import { computed } from "vue";
import {
  VisDonut,
  VisSingleContainer,
  VisTooltip,
} from "@unovis/vue";

import { paletteFor } from "./palette";

const props = withDefaults(
  defineProps<{
    data: T[];
    value: (d: T) => number;
    height?: number;
    palette?: "sequential" | "categorical";
    centralLabel?: string;
    centralSubLabel?: string;
    arcWidth?: number;
  }>(),
  { height: 240, palette: "categorical", arcWidth: 8 },
);

const colors = computed(() => paletteFor(props.palette));
const colorFor = computed(() => (_d: T, i: number) => colors.value[i % colors.value.length]);
</script>

<template>
  <VisSingleContainer :data="data" :height="height">
    <VisDonut
      :value="value"
      :color="colorFor"
      :arc-width="arcWidth"
      :pad-angle="0.01"
      :corner-radius="0"
      :central-label="centralLabel"
      :central-sub-label="centralSubLabel"
      :show-background="false"
    />
    <VisTooltip />
  </VisSingleContainer>
</template>
