<template>
  <Card class="h-full">
    <CardHeader class="px-6 pt-5 pb-3">
      <CardTitle class="text-sm font-medium tracking-tight">{{ title }}</CardTitle>
    </CardHeader>
    <CardContent class="px-6 pb-6 pt-0">
      <div :style="{ height: `${height}px` }">
        <slot v-if="hasData" />
        <div
          v-else
          class="flex h-full flex-col items-center justify-center text-muted-foreground gap-2"
        >
          <component :is="emptyIcon" class="size-6" />
          <span class="text-sm">{{ emptyLabel }}</span>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

<script lang="ts" setup>
import { BarChart3, type LucideIcon } from "lucide-vue-next";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

withDefaults(
  defineProps<{
    title: string;
    hasData: boolean;
    height?: number;
    emptyIcon?: LucideIcon;
    emptyLabel?: string;
  }>(),
  {
    height: 300,
    emptyIcon: () => BarChart3 as unknown as LucideIcon,
    emptyLabel: "No data available",
  },
);
</script>
