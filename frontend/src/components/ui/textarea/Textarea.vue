<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { useVModel } from '@vueuse/core'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
  defaultValue?: string | number
  modelValue?: string | number
}>()

const emits = defineEmits<{
  (e: 'update:modelValue', payload: string | number): void
}>()

const modelValue = useVModel(props, 'modelValue', emits, {
  passive: true,
  defaultValue: props.defaultValue,
})
</script>

<template>
  <textarea
    v-model="modelValue"
    data-slot="textarea"
    :class="cn(
      'flex field-sizing-content min-h-16 w-full bg-muted dark:bg-black/25 px-3 py-2 text-sm text-foreground transition-colors',
      'border border-input rounded-md',
      'placeholder:text-muted-foreground',
      'hover:bg-secondary/60 dark:hover:bg-black/35',
      'focus-visible:outline-none focus-visible:bg-muted dark:focus-visible:bg-black/30 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/30',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'aria-invalid:border-destructive aria-invalid:focus-visible:border-destructive',
      props.class,
    )"
  />
</template>
