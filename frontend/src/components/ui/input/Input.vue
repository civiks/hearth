<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { useVModel } from '@vueuse/core'
import { cn } from '@/lib/utils'

const props = defineProps<{
  defaultValue?: string | number
  modelValue?: string | number
  class?: HTMLAttributes['class']
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
  <input
    v-model="modelValue"
    data-slot="input"
    :class="cn(
      'h-10 w-full min-w-0 dark:bg-secondary bg-muted px-3 text-sm text-foreground transition-colors',
      'border-0 border-b border-input',
      'placeholder:text-muted-foreground',
      'hover:bg-secondary/60',
      'focus-visible:outline-none focus-visible:bg-muted focus-visible:border-primary focus-visible:shadow-[inset_0_-1px_0_hsl(var(--primary))]',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
      'aria-invalid:border-destructive aria-invalid:focus-visible:border-destructive',
      'file:inline-flex file:h-6 file:border-0 file:bg-transparent file:text-sm file:text-foreground',
      props.class,
    )"
  >
</template>
