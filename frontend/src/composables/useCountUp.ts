import { onMounted, ref, watch } from 'vue'

export function useCountUp(source: () => number, duration = 650) {
  const displayed = ref(0)

  function animate(to: number) {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
      displayed.value = to
      return
    }
    const from = displayed.value
    const start = performance.now()
    function step(now: number) {
      const t = Math.min((now - start) / duration, 1)
      displayed.value = Math.round(from + (to - from) * (1 - (1 - t) ** 3))
      if (t < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }

  onMounted(() => animate(source()))
  watch(source, (to) => animate(to))

  return displayed
}
