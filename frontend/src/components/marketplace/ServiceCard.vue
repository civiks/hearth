<template>
  <button
    type="button"
    class="group block w-full text-left bg-card overflow-hidden rounded-lg soft-card hover:soft-card-hover card-lift focus-visible:outline-2 focus-visible:outline-primary"
    @click="$emit('select')"
  >
    <div class="relative aspect-[16/9] overflow-hidden bg-muted">
      <img
        v-if="service.image_url"
        :src="service.image_url"
        :srcset="imageSrcset"
        :sizes="imageSrcset ? '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 400px' : undefined"
        :alt="service.name"
        loading="lazy"
        class="size-full object-cover"
      />
      <!-- Permanent dark scrim spanning the full image — anchors the price/category overlays and lifts text legibility against any photo. -->
      <div
        class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/95 via-black/40 to-black/10"
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
        <span class="inline-flex items-baseline gap-0.5 text-lg font-semibold leading-none">
          <span class="text-[11px] font-normal opacity-80">Rs</span>
          {{ service.base_price }}
        </span>
        <span class="inline-flex items-center gap-1 text-[11px] opacity-70">
          <Clock class="size-2.5" />
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
import { Clock, Star } from "lucide-vue-next";
import { computed } from "vue";

import { Badge } from "@/components/ui/badge";

const props = defineProps<{
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

// Builds a responsive srcset from an Unsplash URL by swapping the `w=` param.
// Returns undefined for non-Unsplash URLs so the browser falls back to `src`.
const SRCSET_WIDTHS = [320, 480, 768, 960];
const imageSrcset = computed(() => {
  const url = props.service.image_url;
  if (!url || !url.includes("images.unsplash.com") || !/w=\d+/.test(url)) {
    return undefined;
  }
  return SRCSET_WIDTHS.map((w) => `${url.replace(/w=\d+/, `w=${w}`)} ${w}w`).join(", ");
});
</script>
