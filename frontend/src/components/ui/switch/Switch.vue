<script setup lang="ts">
import type { SwitchRootEmits, SwitchRootProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import {
  SwitchRoot,
  SwitchThumb,
  useForwardPropsEmits,
} from 'reka-ui'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<SwitchRootProps & {
  class?: HTMLAttributes['class']
  size?: 'sm' | 'default'
}>(), {
  size: 'default',
})

const emits = defineEmits<SwitchRootEmits>()

const delegatedProps = reactiveOmit(props, 'class', 'size')

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<!--
  Track: 48×24 default, 32×16 small. Rounded-full.
  Off: gray-50 (#8d8d8d). On: primary blue. Hover deepens each by one step.
  Thumb: white circle, 18px default, 10px small, with a 3px inset from the track edge.
  Focus: 2px solid primary outline at 2px offset OUTSIDE the toggle/
-->
<template>
  <SwitchRoot
    v-slot="slotProps"
    data-slot="switch"
    :data-size="size"
    v-bind="forwarded"
    :class="cn(
      'group/switch peer relative inline-flex shrink-0 items-center cursor-pointer rounded-full border border-transparent outline-none transition-colors',
      'data-[size=default]:h-6 data-[size=default]:w-12 data-[size=sm]:h-4 data-[size=sm]:w-8',
      'data-[state=unchecked]:bg-[#8d8d8d] data-[state=unchecked]:hover:bg-[#6f6f6f]',
      'data-[state=checked]:bg-primary data-[state=checked]:hover:bg-[#0353e9]',
      'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary',
      'data-[disabled]:cursor-not-allowed data-[disabled]:opacity-50',
      props.class,
    )"
  >
    <SwitchThumb
      data-slot="switch-thumb"
      class="pointer-events-none block bg-white rounded-full transition-transform ml-[3px] group-data-[size=default]/switch:size-[18px] group-data-[size=sm]/switch:size-[10px] group-data-[state=unchecked]/switch:translate-x-0 group-data-[size=default]/switch:group-data-[state=checked]/switch:translate-x-[24px] group-data-[size=sm]/switch:group-data-[state=checked]/switch:translate-x-[16px]"
    >
      <slot name="thumb" v-bind="slotProps" />
    </SwitchThumb>
  </SwitchRoot>
</template>
