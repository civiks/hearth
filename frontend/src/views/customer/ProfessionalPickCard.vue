<template>
  <button
    type="button"
    class="w-full text-left rounded-lg p-3 flex items-center gap-3 bg-card press"
    :class="selected ? 'soft-card-selected' : 'soft-card hover:soft-card-hover'"
    @click="$emit('select')"
  >
    <span class="relative">
      <ProfessionalAvatar
        :name="professional.full_name"
        :src="professional.avatar_url"
        class="size-12 shrink-0"
      />
      <span
        v-if="selected"
        class="absolute -bottom-1 -right-1 inline-flex size-3.5 items-center justify-center rounded-full bg-primary text-primary-foreground ring-2 ring-card"
      >
        <PhCheck class="size-3" />
      </span>
    </span>
    <div class="flex-1 min-w-0">
      <div class="flex items-center justify-between gap-2">
        <span class="text-sm font-medium tracking-tight truncate">{{ professional.full_name }}</span>
        <span v-if="professional.rating != null" class="flex items-center gap-1 text-xs tabular-nums">
          <PhStar weight="fill" class="size-3 text-amber-400" />
          <span class="font-medium tracking-tight">{{ professional.rating.toFixed(1) }}</span>
          <span class="text-muted-foreground">({{ professional.review_count ?? 0 }})</span>
        </span>
      </div>
      <p v-if="professional.description" class="text-xs text-muted-foreground tracking-tight leading-relaxed line-clamp-1">
        {{ professional.description }}
      </p>
      <p class="text-[11px] font-medium tracking-tight tabular-nums text-muted-foreground mt-0.5">
        {{ professional.experience ?? 0 }} years experience
      </p>
    </div>
  </button>
</template>

<script lang="ts" setup>
import {
  PhCheck,
  PhStar,
} from '@phosphor-icons/vue';

import ProfessionalAvatar from "@/components/marketplace/ProfessionalAvatar.vue";

defineProps<{
  professional: {
    id: number;
    full_name: string;
    avatar_url?: string | null;
    rating?: number | null;
    review_count?: number | null;
    experience?: number | null;
    description?: string | null;
  };
  selected: boolean;
}>();

defineEmits<{ select: [] }>();
</script>
