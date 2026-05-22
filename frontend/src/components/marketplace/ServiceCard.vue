<template>
  <button
    type="button"
    class="group block w-full text-left bg-card overflow-hidden focus-visible:outline-2 focus-visible:outline-primary"
    @click="$emit('select')"
  >
    <div class="relative aspect-[16/10] overflow-hidden bg-muted">
      <img
        v-if="service.image_url"
        :src="service.image_url"
        :alt="service.name"
        loading="lazy"
        class="size-full object-cover"
      />
      <!-- Permanent dark scrim at the bottom - headroom for the price overlay -->
      <div
        class="pointer-events-none absolute inset-x-0 bottom-0 h-2/5 bg-gradient-to-t from-black/85 via-black/40 to-transparent"
        aria-hidden="true"
      />
      <!-- Hover overlay -->
      <div
        class="pointer-events-none absolute inset-0 bg-black/20 opacity-0 transition-opacity duration-150 group-hover:opacity-100"
        aria-hidden="true"
      />
      <Badge
        v-if="service.category"
        variant="secondary"
        class="absolute top-2 left-2 bg-background/90 text-foreground border-0 backdrop-blur text-[11px] px-1.5 py-0"
      >
        {{ service.category }}
      </Badge>
      <!-- Price overlaid on the image bottom — primary at-a-glance info -->
      <div class="absolute bottom-2 left-3 right-3 flex items-end justify-between text-white">
        <span class="inline-flex items-center gap-0.5 text-lg font-semibold leading-none">
          <IndianRupee class="size-4" :stroke-width="2.25" />
          {{ service.base_price }}
        </span>
        <span class="inline-flex items-center gap-1 text-[11px] opacity-90">
          <Clock class="size-3" />
          {{ service.time_required }} min
        </span>
      </div>
    </div>

    <div class="p-3 space-y-1">
      <div class="flex items-start justify-between gap-2">
        <h3 class="text-sm font-medium line-clamp-1 flex-1">{{ service.name }}</h3>
        <span
          v-if="service.rating != null"
          class="inline-flex items-center gap-1 text-xs shrink-0"
        >
          <Star class="size-3 fill-amber-400 text-amber-400" />
          <span class="font-medium">{{ service.rating.toFixed(1) }}</span>
          <span v-if="service.review_count != null" class="text-muted-foreground">
            ({{ service.review_count }})
          </span>
        </span>
      </div>

      <p class="text-xs text-muted-foreground line-clamp-2 min-h-8">
        {{ service.description ?? "" }}
      </p>
    </div>
  </button>
</template>

<script lang="ts" setup>
import { Clock, IndianRupee, Star } from "lucide-vue-next";

import { Badge } from "@/components/ui/badge";

defineProps<{
  service: {
    id: number;
    name: string;
    description?: string | null;
    base_price: number;
    time_required: number;
    category?: string | null;
    image_url?: string;
    rating?: number;
    review_count?: number;
  };
}>();

defineEmits<{ select: [] }>();
</script>
