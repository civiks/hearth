<script setup lang="ts">
import { SplitterPanel, type SplitterPanelProps } from "reka-ui";
import { ref } from "vue";

defineProps<SplitterPanelProps>();

/**
 * Mirrors the methods reka's SplitterPanel exposes via `__expose`, so a
 * `ref` on this wrapper still lets the parent drive `expand` / `collapse`
 * / `resize` programmatically.
 */
export interface SplitterPanelHandle {
  collapse: () => void;
  expand: () => void;
  resize: (size: number) => void;
  getSize: () => number;
}

const inner = ref<SplitterPanelHandle | null>(null);

defineExpose<SplitterPanelHandle>({
  collapse: () => inner.value?.collapse(),
  expand: () => inner.value?.expand(),
  resize: (size) => inner.value?.resize(size),
  getSize: () => inner.value?.getSize() ?? 0,
});
</script>

<template>
  <SplitterPanel ref="inner" v-bind="$props">
    <slot />
  </SplitterPanel>
</template>
