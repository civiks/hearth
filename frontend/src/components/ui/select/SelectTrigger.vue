<script setup lang="ts">
import type { SelectTriggerProps } from 'reka-ui'

import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { ChevronDownIcon } from '@lucide/vue'
import { SelectIcon, SelectTrigger, useForwardProps } from 'reka-ui'
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<SelectTriggerProps & { class?: HTMLAttributes['class'], size?: 'sm' | 'default' }>(),
  { size: 'default' },
)

const delegatedProps = reactiveOmit(props, 'class', 'size')
const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <SelectTrigger
    data-slot="select-trigger"
    :data-size="size"
    v-bind="forwardedProps"
    :class="cn(
      'flex w-full items-center justify-between gap-2 whitespace-nowrap bg-muted dark:bg-black/25 px-3 text-sm text-foreground select-none transition-colors',
      'border border-input rounded-md',
      'data-[size=default]:h-10 data-[size=sm]:h-8',
      'data-placeholder:text-muted-foreground',
      'hover:bg-secondary/60 dark:hover:bg-black/35',
      'focus-visible:outline-none focus-visible:bg-muted dark:focus-visible:bg-black/30 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/30',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'aria-invalid:border-destructive aria-invalid:focus-visible:border-destructive',
      '[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=size-])]:size-3.5',
      '*:data-[slot=select-value]:line-clamp-1 *:data-[slot=select-value]:flex *:data-[slot=select-value]:items-center *:data-[slot=select-value]:gap-1.5',
      props.class,
    )"
  >
    <slot />
    <SelectIcon as-child>
      <ChevronDownIcon class="text-muted-foreground size-3.5 pointer-events-none" />
    </SelectIcon>
  </SelectTrigger>
</template>
