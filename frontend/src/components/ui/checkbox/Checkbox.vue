<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { CheckboxIndicator, CheckboxRoot, useForwardPropsEmits } from 'reka-ui'
import { Check } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
  checked?: boolean | 'indeterminate'
  defaultChecked?: boolean
  required?: boolean
  disabled?: boolean
  value?: string
  name?: string
}>()

const emits = defineEmits<{ 'update:checked': [value: boolean] }>()
const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <CheckboxRoot
    v-bind="forwarded"
    :class="cn(
      'peer size-4 shrink-0 rounded-sm border border-input bg-background ring-offset-background transition-colors',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'data-[state=checked]:bg-primary data-[state=checked]:border-primary data-[state=checked]:text-primary-foreground',
      props.class
    )"
  >
    <CheckboxIndicator class="flex items-center justify-center text-current">
      <Check class="size-3" :stroke-width="3" />
    </CheckboxIndicator>
  </CheckboxRoot>
</template>
