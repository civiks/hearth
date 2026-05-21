<template>
  <section class="border-b bg-card">
    <div class="px-6 py-6 space-y-3">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
            <MapPin class="size-3.5" />
            Bangalore — Indiranagar
            <button class="underline underline-offset-2 hover:text-foreground ml-1">
              change
            </button>
          </div>
          <h1 class="text-2xl font-light tracking-tight mt-1">
            Trusted home services on demand
          </h1>
          <p class="text-xs text-muted-foreground mt-0.5">
            {{ bookedToday }} services booked in your area this week.
          </p>
        </div>
        <div class="relative w-full sm:w-80">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            :model-value="modelValue"
            placeholder="Search for plumbing, AC repair, cleaning…"
            class="pl-9 h-10"
            @update:model-value="$emit('update:modelValue', String($event))"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { MapPin, Search } from "lucide-vue-next";
import { computed } from "vue";

import { Input } from "@/components/ui/input";

const props = defineProps<{ modelValue: string; bookingsThisWeek?: number }>();
defineEmits<{ "update:modelValue": [value: string] }>();

const bookedToday = computed(() => props.bookingsThisWeek ?? 147);
</script>
