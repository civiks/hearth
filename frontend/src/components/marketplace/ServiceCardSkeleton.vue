<template>
  <div class="bg-card overflow-hidden">
    <Skeleton class="aspect-[16/10] w-full rounded-none" />
    <div class="p-3 space-y-2">
      <div class="flex items-center justify-between gap-2">
        <Skeleton class="h-3.5 w-2/3 rounded-none" />
        <Skeleton class="h-3 w-10 rounded-none" />
      </div>
      <Skeleton class="h-3 w-full rounded-none" />
      <div class="flex items-center justify-between pt-1.5">
        <Skeleton class="h-3 w-10 rounded-none" />
        <Skeleton class="h-3 w-14 rounded-none" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Skeleton } from "@/components/ui/skeleton";
</script>
