<script lang="ts" setup>
import type { ToasterProps } from 'vue-sonner'

import {
  PhCheckCircle,
  PhInfo,
  PhCircleNotch,
  PhWarningCircle,
  PhXCircle,
  PhX,
} from '@phosphor-icons/vue'
import { Toaster as Sonner } from 'vue-sonner'
import { cn } from '@/lib/utils'

const props = defineProps<ToasterProps>()
</script>

<template>
  <Sonner
    :class="cn('toaster group', props.class)"
    :style="{
      '--normal-bg': 'hsl(var(--card))',
      '--normal-text': 'hsl(var(--card-foreground))',
      '--normal-border': 'hsl(var(--border))',
      '--border-radius': '1rem',
      '--width': '380px',
    }"
    v-bind="props"
  >
    <template #success-icon>
      <PhCheckCircle class="size-5" weight="bold" />
    </template>
    <template #info-icon>
      <PhInfo class="size-5" weight="bold" />
    </template>
    <template #warning-icon>
      <PhWarningCircle class="size-5" weight="bold" />
    </template>
    <template #error-icon>
      <PhXCircle class="size-5" weight="bold" />
    </template>
    <template #loading-icon>
      <div>
        <PhCircleNotch class="size-5 animate-spin" weight="bold" />
      </div>
    </template>
    <template #close-icon>
      <PhX class="size-[1.05rem]" weight="bold" />
    </template>
  </Sonner>
</template>
