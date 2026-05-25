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
      'flex field-sizing-content min-h-16 w-full dark:bg-secondary bg-muted px-3 py-2 text-sm text-foreground transition-colors',
      'border-0 border-b border-input',
      'placeholder:text-muted-foreground',
      'hover:bg-secondary/60',
      'focus-visible:outline-none dark:focus-visible:bg-secondary focus-visible:bg-muted focus-visible:border-primary focus-visible:shadow-[inset_0_-1px_0_hsl(var(--primary))]',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'aria-invalid:border-destructive aria-invalid:focus-visible:border-destructive',
      props.class,
    )"
  />
</template>
