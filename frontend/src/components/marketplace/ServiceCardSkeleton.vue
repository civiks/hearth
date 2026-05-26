<template>
  <div class="bg-card overflow-hidden rounded-lg soft-card">
    <Skeleton class="aspect-[16/9] w-full rounded-none" />
    <div class="p-3 space-y-2">
      <div class="flex items-center justify-between gap-2">
        <Skeleton class="h-3.5 w-2/3" />
        <Skeleton class="h-3 w-10" />
      </div>
      <Skeleton class="h-3 w-full" />
      <div class="flex items-center justify-between pt-1.5">
        <Skeleton class="h-3 w-10" />
        <Skeleton class="h-3 w-14" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Skeleton } from "@/components/ui/skeleton";
</script>
