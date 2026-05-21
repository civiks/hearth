<template>
  <button
    type="button"
    class="w-full text-left border bg-card p-3 flex items-center gap-3 transition hover:border-primary/60"
    :class="selected ? 'border-primary ring-2 ring-primary/15' : ''"
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
        class="absolute -bottom-1 -right-1 inline-flex size-4 items-center justify-center bg-primary text-primary-foreground"
      >
        <Check class="size-3" />
      </span>
    </span>
    <div class="flex-1 min-w-0">
      <div class="flex items-center justify-between gap-2">
        <span class="text-sm font-medium truncate">{{ professional.full_name }}</span>
        <span v-if="professional.rating != null" class="flex items-center gap-1 text-xs">
          <Star class="size-3 fill-amber-400 text-amber-400" />
          <span class="font-medium">{{ professional.rating.toFixed(1) }}</span>
          <span class="text-muted-foreground">({{ professional.review_count ?? 0 }})</span>
        </span>
      </div>
      <p v-if="professional.description" class="text-xs text-muted-foreground line-clamp-1">
        {{ professional.description }}
      </p>
      <p class="text-[11px] text-muted-foreground mt-0.5">
        {{ professional.experience ?? 0 }} years experience
      </p>
    </div>
  </button>
</template>

<script lang="ts" setup>
import { Check, Star } from "lucide-vue-next";

import ProfessionalAvatar from "@/components/marketplace/ProfessionalAvatar.vue";

defineProps<{
  professional: {
    id: number;
    full_name: string;
    avatar_url?: string;
    rating?: number | null;
    review_count?: number | null;
    experience?: number | null;
    description?: string | null;
  };
  selected: boolean;
}>();

defineEmits<{ select: [] }>();
</script>
