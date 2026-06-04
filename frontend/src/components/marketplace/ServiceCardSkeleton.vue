<template>
  <div>
    <Skeleton class="aspect-[16/9] w-full rounded-xl" />
    <div class="mt-2 space-y-2">
      <Skeleton class="h-3.5 w-3/4" />
      <div class="flex items-center justify-between">
        <Skeleton class="h-4 w-12" />
        <Skeleton class="h-3 w-8" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Skeleton } from "@/components/ui/skeleton";
</script>
