<template>
  <button
    type="button"
    class="group relative block w-full text-left rounded-xl overflow-hidden bg-card soft-card hover:soft-card-hover press focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
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
      <div
        class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/80 via-black/25 to-transparent transition-opacity duration-300 group-hover:opacity-65"
        aria-hidden="true"
      />

      <span
        v-if="badge"
        :class="[
          'absolute left-2 top-2 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold leading-none shadow-sm backdrop-blur-sm',
          badge.class,
        ]"
      >
        <component :is="badge.icon" class="size-3" weight="fill" />
        {{ badge.label }}
      </span>

      <span
        v-if="service.rating != null"
        class="absolute right-2 bottom-2 inline-flex items-center gap-1 rounded-full bg-black/55 px-1.5 py-0.5 text-[11px] font-medium tabular-nums text-white backdrop-blur-sm"
      >
        <PhStar weight="fill" class="size-3 text-amber-400" />
        {{ service.rating.toFixed(1) }}
        <span v-if="service.review_count" class="text-white/70">({{ service.review_count }})</span>
      </span>
    </div>

    <div class="relative px-4 pt-3.5 pb-5 overflow-hidden">
      <template v-if="service.image_url">
        <img
          :src="service.image_url"
          aria-hidden="true"
          loading="lazy"
          class="pointer-events-none absolute inset-x-0 -top-[80%] h-[180%] w-full scale-150 object-cover object-bottom blur-3xl saturate-[1.7]"
        />
        <div class="image-wash pointer-events-none absolute inset-0" aria-hidden="true" />
      </template>

      <h3 class="relative text-[15px] font-semibold tracking-[-0.01em] leading-snug line-clamp-2">{{ service.name }}</h3>

      <p v-if="service.description" class="relative mt-1 text-xs text-muted-foreground leading-snug line-clamp-1">
        {{ service.description }}
      </p>

      <div class="relative mt-3.5 flex items-end justify-between gap-3">
        <div class="inline-flex items-center gap-0.5 tabular-nums text-foreground">
          <PhCurrencyInr class="size-3.5" weight="bold" />
          <span class="text-lg font-bold leading-none tracking-tight">{{ service.base_price }}</span>
        </div>

        <div
          v-if="service.category || service.time_required"
          class="flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground"
        >
          <span v-if="service.category" class="truncate">{{ service.category }}</span>
          <span v-if="service.category && service.time_required" aria-hidden="true" class="text-muted-foreground/50">·</span>
          <span v-if="service.time_required" class="inline-flex shrink-0 items-center gap-0.5">
            <PhClock class="size-3" weight="bold" />
            {{ durationLabel }}
          </span>
        </div>
      </div>
    </div>
  </button>
</template>

<script lang="ts" setup>
import {
  PhClock,
  PhCurrencyInr,
  PhStar,
  PhTrendUp,
  PhSparkle,
  PhCrown,
} from '@phosphor-icons/vue';
import { computed, type Component } from "vue";

type BadgeKind = "popular" | "top-rated" | "new";

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
  badge?: BadgeKind | null;
}>();

defineEmits<{ select: [] }>();

const BADGES: Record<BadgeKind, { label: string; icon: Component; class: string }> = {
  popular: { label: "Most booked", icon: PhTrendUp, class: "bg-white/90 text-zinc-900" },
  "top-rated": { label: "Top rated", icon: PhCrown, class: "bg-amber-400/95 text-amber-950" },
  new: { label: "New", icon: PhSparkle, class: "bg-primary text-primary-foreground" },
};

const badge = computed(() => (props.badge ? BADGES[props.badge] : null));

const durationLabel = computed(() => {
  const mins = props.service.time_required;
  if (!mins) return "";
  if (mins < 60) return `${mins} min`;
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return m ? `${h}h ${m}m` : `${h}h`;
});

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
