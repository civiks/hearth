<script lang="ts" setup>
import type { ToasterProps } from 'vue-sonner'

import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
  XIcon,
} from '@lucide/vue'
import { Toaster as Sonner } from 'vue-sonner'
import { cn } from '@/lib/utils'

const props = defineProps<ToasterProps>()
</script>

<template>
  <Sonner
    :class="cn('toaster group', props.class)"
    :style="{
      // Default toast (no rich-colors) — popover surface, foreground text, border token.
      '--normal-bg': 'hsl(var(--popover))',
      '--normal-text': 'hsl(var(--popover-foreground))',
      '--normal-border': 'hsl(var(--border))',
      // Status variants — bg/text are pale tints, border = corresponding `*-strong` token.
      '--success-bg': 'hsl(var(--toast-success-bg))',
      '--success-border': 'hsl(var(--success-strong))',
      '--success-text': 'hsl(var(--toast-success-text))',
      '--error-bg': 'hsl(var(--toast-error-bg))',
      '--error-border': 'hsl(var(--destructive))',
      '--error-text': 'hsl(var(--toast-error-text))',
      '--warning-bg': 'hsl(var(--toast-warning-bg))',
      '--warning-border': 'hsl(var(--warning-strong))',
      '--warning-text': 'hsl(var(--toast-warning-text))',
      '--info-bg': 'hsl(var(--toast-info-bg))',
      '--info-border': 'hsl(var(--info-strong))',
      '--info-text': 'hsl(var(--toast-info-text))',
    }"
    v-bind="props"
  >
    <template #success-icon>
      <CircleCheckIcon class="size-3.5" />
    </template>
    <template #info-icon>
      <InfoIcon class="size-3.5" />
    </template>
    <template #warning-icon>
      <TriangleAlertIcon class="size-3.5" />
    </template>
    <template #error-icon>
      <OctagonXIcon class="size-3.5" />
    </template>
    <template #loading-icon>
      <div>
        <Loader2Icon class="size-3.5 animate-spin" />
      </div>
    </template>
    <template #close-icon>
      <XIcon class="size-3.5" />
    </template>
  </Sonner>
</template>
