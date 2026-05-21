<template>
  <Card>
    <CardContent class="flex flex-col gap-3 px-4 py-3">
      <span
        class="text-[11px] font-normal uppercase tracking-wide text-muted-foreground leading-none"
      >
        {{ label }}
      </span>
      <span
        class="text-4xl font-light leading-none text-foreground tracking-tight"
      >
        <slot>{{ value }}</slot>
      </span>
      <span v-if="$slots.hint" class="text-[11px] text-muted-foreground leading-tight -mt-1">
        <slot name="hint" />
      </span>
    </CardContent>
  </Card>
</template>

<script lang="ts" setup>
import { Card, CardContent } from "@/components/ui/card";

defineProps<{ label: string; value?: string | number }>();
</script>
