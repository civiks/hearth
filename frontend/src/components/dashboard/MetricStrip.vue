<script setup lang="ts">
import {
  PhArrowRight,
} from '@phosphor-icons/vue';
import { RouterLink, type RouteLocationRaw } from "vue-router";

import { Card, CardContent, CardHeader } from "@/components/ui/card";

export interface StripTile {
  label: string;
  value: string | number;
  to?: RouteLocationRaw;
  viewAllLabel?: string;
}

defineProps<{
  title?: string;
  tiles: StripTile[];
}>();
</script>

<template>
  <Card>
    <CardHeader v-if="title" class="pb-1">
      <h3 class="text-sm font-medium leading-tight">{{ title }}</h3>
    </CardHeader>
    <CardContent
      :class="[
        'grid grid-cols-2 gap-x-6 gap-y-5',
        tiles.length >= 4 ? 'sm:grid-cols-4' : `sm:grid-cols-${tiles.length}`,
      ]"
    >
      <div v-for="tile in tiles" :key="tile.label" class="min-w-0">
        <p class="text-xs text-muted-foreground truncate">{{ tile.label }}</p>
        <p class="text-3xl font-light leading-tight tabular-nums mt-1 truncate">
          {{ tile.value }}
        </p>
        <RouterLink
          v-if="tile.to"
          :to="tile.to"
          class="mt-1.5 inline-flex items-center gap-1 text-xs text-primary hover:underline underline-offset-4 focus-visible:outline-none focus-visible:underline"
        >
          {{ tile.viewAllLabel ?? "View all" }}
          <PhArrowRight class="size-3.5" weight="bold" />
        </RouterLink>
      </div>
    </CardContent>
  </Card>
</template>
