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
      'h-10 w-full min-w-0 bg-muted dark:bg-input px-3 text-sm text-foreground transition-colors',
      'border border-input rounded-md input-inset',
      'placeholder:text-[hsl(0,0%,58%)] dark:placeholder:text-muted-foreground',
      'hover:bg-input-hover',
      'focus-visible:outline-none focus-visible:bg-muted dark:focus-visible:bg-input focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/30',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
      'aria-invalid:border-destructive aria-invalid:focus-visible:border-destructive',
      'file:inline-flex file:h-6 file:border-0 file:bg-transparent file:text-sm file:text-foreground',
      props.class,
    )"
  >
</template>
