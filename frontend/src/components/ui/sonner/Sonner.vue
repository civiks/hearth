<script lang="ts" setup>
import type { ToasterProps } from 'vue-sonner'

import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
  XIcon,
} from 'lucide-vue-next'
import { Toaster as Sonner } from 'vue-sonner'
import { cn } from '@/lib/utils'

const props = defineProps<ToasterProps>()
</script>

<template>
  <Sonner
    :class="cn('toaster group', props.class)"
    :style="{
      // Default toast (no rich-colors): white surface, gray-100 text, gray-20 border.
      '--normal-bg': '#ffffff',
      '--normal-text': '#161616',
      '--normal-border': '#e0e0e0',
      // Carbon notification palette for rich-colors variants.
      '--success-bg': '#defbe6',
      '--success-border': '#198038',
      '--success-text': '#0e6027',
      '--error-bg': '#fff1f1',
      '--error-border': '#da1e28',
      '--error-text': '#a2191f',
      '--warning-bg': '#fdf6dd',
      '--warning-border': '#b28600',
      '--warning-text': '#684e00',
      '--info-bg': '#edf5ff',
      '--info-border': '#0043ce',
      '--info-text': '#002d9c',
      '--border-radius': '0px',
    }"
    v-bind="props"
  >
    <template #success-icon>
      <CircleCheckIcon class="size-4" />
    </template>
    <template #info-icon>
      <InfoIcon class="size-4" />
    </template>
    <template #warning-icon>
      <TriangleAlertIcon class="size-4" />
    </template>
    <template #error-icon>
      <OctagonXIcon class="size-4" />
    </template>
    <template #loading-icon>
      <div>
        <Loader2Icon class="size-4 animate-spin" />
      </div>
    </template>
    <template #close-icon>
      <XIcon class="size-4" />
    </template>
  </Sonner>
</template>
