<template>
  <div
    class="relative overflow-hidden transition-[height] duration-[280ms] ease-[cubic-bezier(0.32,0.72,0,1)] motion-reduce:transition-none"
    :style="ready ? { height: `${height}px` } : undefined"
  >
    <div ref="measure">
      <Transition name="dm">
        <slot />
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useElementSize } from "@vueuse/core";
import { onMounted, onUnmounted, ref, watch } from "vue";
import { useConfirm } from "@/composables/useConfirm";

const { registerHost, unregisterHost } = useConfirm();
onMounted(registerHost);
onUnmounted(unregisterHost);

const measure = ref<HTMLElement | null>(null);
const { height } = useElementSize(measure);

const ready = ref(false);
const stop = watch(height, (h) => {
  if (h > 0) {
    ready.value = true;
    stop();
  }
});
</script>

<style>
.dm-enter-active,
.dm-leave-active {
  transform-origin: top center;
  transition:
    opacity 200ms cubic-bezier(0.32, 0.72, 0, 1),
    transform 280ms cubic-bezier(0.32, 0.72, 0, 1);
}
.dm-leave-active {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}
.dm-enter-from,
.dm-leave-to {
  opacity: 0;
  transform: scale(0.96);
}
@media (prefers-reduced-motion: reduce) {
  .dm-enter-active,
  .dm-leave-active {
    transition: opacity 100ms linear;
  }
  .dm-enter-from,
  .dm-leave-to {
    transform: none;
  }
}
</style>
