<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import {
  PhArrowRight,
} from '@phosphor-icons/vue';
import { RouterLink, type RouteLocationRaw } from "vue-router";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils";

withDefaults(
  defineProps<{
    title: string;
    subtitle?: string;
    viewAllTo?: RouteLocationRaw;
    viewAllLabel?: string;
    bodyClass?: string;
    chart?: boolean;
    class?: HTMLAttributes["class"];
  }>(),
  { viewAllLabel: "View all" },
);
</script>

<template>
  <Card :class="$props.class">
    <CardHeader class="flex flex-row items-start justify-between gap-3 pb-2 sm:pb-3">
      <div class="min-w-0">
        <h3 class="text-sm font-semibold leading-tight truncate">
          <slot name="title">{{ title }}</slot>
        </h3>
        <p v-if="subtitle" class="text-xs text-muted-foreground mt-0.5 truncate">
          {{ subtitle }}
        </p>
      </div>
      <div class="shrink-0">
        <slot name="action">
          <RouterLink
            v-if="viewAllTo"
            :to="viewAllTo"
            :aria-label="viewAllLabel"
            class="text-xs text-primary inline-flex items-center gap-1 hover:underline underline-offset-4 focus-visible:outline-none focus-visible:underline"
          >
            <span class="sm:hidden md:inline">{{ viewAllLabel }}</span>
            <PhArrowRight class="size-3.5" />
          </RouterLink>
        </slot>
      </div>
    </CardHeader>
    <CardContent :class="cn('relative', chart && 'chart', bodyClass)">
      <slot />
    </CardContent>
  </Card>
</template>
