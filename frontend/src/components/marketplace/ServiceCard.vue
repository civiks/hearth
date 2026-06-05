<template>
  <button
    type="button"
    class="group relative block w-full text-left rounded-xl overflow-hidden bg-card soft-card hover:soft-card-hover transition-shadow focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
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
        class="size-full object-cover transition-transform duration-300 group-hover:scale-[1.04]"
      />
      <div
        class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/80 via-black/25 to-transparent"
        aria-hidden="true"
      />
    </div>

    <div class="pointer-events-none absolute inset-0 rounded-xl ring-1 ring-inset ring-border z-10" aria-hidden="true" />

    <div class="px-3 pb-3 mt-2">
      <h3 class="text-sm font-medium tracking-tight leading-snug truncate">{{ service.name }}</h3>

      <div class="mt-1 flex items-center justify-between gap-2">
        <span class="inline-flex items-end gap-0.5 text-base font-semibold tabular-nums">
          <span class="text-[11px] font-normal leading-none text-muted-foreground mb-px">Rs</span>
          <span class="leading-none">{{ service.base_price }}</span>
        </span>
        <span
          v-if="service.rating != null"
          class="inline-flex items-center gap-1 text-xs tabular-nums shrink-0"
        >
          <Star class="size-3 fill-amber-400 text-amber-400" />
          <span class="font-medium">{{ service.rating.toFixed(1) }}</span>
        </span>
      </div>
    </div>
  </button>
</template>

<script lang="ts" setup>
import { Star } from "lucide-vue-next";
import { computed } from "vue";

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
