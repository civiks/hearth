<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { CheckboxIndicator, CheckboxRoot } from 'reka-ui'
import { reactiveOmit } from '@vueuse/core'
import {
  PhCheck,
} from '@phosphor-icons/vue'
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

const emits = defineEmits<{ 'update:checked': [value: boolean | 'indeterminate'] }>()

const delegatedProps = reactiveOmit(props, 'class', 'checked', 'defaultChecked')
</script>

<template>
  <CheckboxRoot
    v-bind="delegatedProps"
    :model-value="checked"
    :default-value="defaultChecked"
    :class="cn(
      'peer size-3.5 shrink-0 rounded-sm border border-input bg-background ring-offset-background transition-colors',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'data-[state=checked]:bg-primary data-[state=checked]:border-primary data-[state=checked]:text-primary-foreground',
      props.class
    )"
    @update:model-value="emits('update:checked', $event)"
  >
    <CheckboxIndicator class="flex items-center justify-center text-current">
      <PhCheck class="size-3" weight="bold" />
    </CheckboxIndicator>
  </CheckboxRoot>
</template>
