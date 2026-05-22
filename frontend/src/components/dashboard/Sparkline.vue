<script setup lang="ts">
import { computed } from "vue";
import { VisLine, VisXYContainer } from "@unovis/vue";

import { sequentialPalette } from "@/components/charts/palette";

const props = withDefaults(
  defineProps<{
    data: number[];
    height?: number;
    color?: string;
  }>(),
  { height: 32 },
);

const points = computed(() => props.data.map((v, i) => ({ i, v })));
const stroke = computed(() => props.color ?? sequentialPalette()[0] ?? "currentColor");
</script>

<template>
  <div class="chart">
    <VisXYContainer
      :data="points"
      :height="height"
      :margin="{ top: 2, right: 2, bottom: 2, left: 2 }"
    >
      <VisLine
        :x="(d: { i: number }) => d.i"
        :y="(d: { v: number }) => d.v"
        :color="stroke"
        :line-width="1.5"
      />
    </VisXYContainer>
  </div>
</template>
