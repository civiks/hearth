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
      <!-- scrim on hover: strong gray gradient from the bottom -->
      <div
        class="pointer-events-none absolute inset-0 bg-gradient-to-t from-foreground/50 via-foreground/20 to-transparent opacity-0 transition-opacity duration-150 ease-out group-hover:opacity-100"
        aria-hidden="true"
      />
      <Badge
        v-if="service.category"
        variant="secondary"
        class="absolute top-2 left-2 bg-white/90 text-foreground border-0 backdrop-blur text-[11px] px-1.5 py-0"
      >
        {{ service.category }}
      </Badge>
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

      <p v-if="service.description" class="text-xs text-muted-foreground line-clamp-1">
        {{ service.description }}
      </p>

      <div class="flex items-center justify-between pt-1.5 text-xs">
        <span class="text-muted-foreground inline-flex items-center gap-1">
          <Clock class="size-3" />
          {{ service.time_required }}m
        </span>
        <span class="font-medium inline-flex items-center gap-0.5">
          <IndianRupee class="size-3" />
          {{ service.base_price }}
        </span>
      </div>
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
