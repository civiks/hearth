import { ref } from 'vue'

const open = ref(false)

export function useSettingsDrawer() {
  return {
    open,
    show: () => { open.value = true },
  }
}
