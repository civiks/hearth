<template>
  <button
    type="button"
    class="w-full text-left bg-card rounded-lg soft-card hover:soft-card-hover transition-shadow overflow-hidden flex items-stretch focus-visible:outline-2 focus-visible:outline-primary"
    :class="cancelled ? 'opacity-60' : ''"
    @click="$emit('open')"
  >
    <!-- Service thumbnail -->
    <div class="relative w-16 sm:w-20 shrink-0 bg-muted self-stretch overflow-hidden">
      <img
        v-if="service?.image_url"
        :src="service.image_url"
        :alt="request.service_name ?? 'Service'"
        loading="lazy"
        class="size-full object-cover"
      />
      <div v-else class="size-full flex items-center justify-center">
        <PhImage class="size-5 text-muted-foreground/40" weight="bold" />
      </div>
      <div
        class="absolute bottom-0 inset-x-0 py-1 text-center text-[9px] font-semibold uppercase tracking-wider"
        :class="statusStripClass"
      >{{ statusLabel }}</div>
    </div>

    <!-- Content -->
    <div class="flex-1 px-4 py-3 min-w-0 flex items-center gap-3">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <p class="text-sm font-medium tracking-tight truncate">{{ request.service_name }}</p>
        </div>
        <div v-if="request.scheduled_time" class="flex items-center gap-1 mt-1 text-xs tracking-tight tabular-nums text-muted-foreground">
          <PhCalendarDots class="size-3 shrink-0" weight="bold" />
          <span>{{ formatSmartDateTime(request.scheduled_time) }}</span>
        </div>
        <div class="flex items-center gap-1.5 mt-1 text-xs tracking-tight text-muted-foreground truncate">
          <template v-if="professional">
            <Avatar :name="professional.full_name" :src="professional.avatar_url" size="size-4 shrink-0" fallback-class="text-[8px]" />
            <span class="truncate">{{ professional.full_name }}</span>
            <span v-if="professional.rating != null" class="inline-flex items-center gap-0.5 shrink-0 tabular-nums">
              <PhStar class="size-3 text-amber-400" weight="fill" />
              {{ professional.rating.toFixed(1) }}
            </span>
          </template>
          <template v-else-if="!cancelled">
            <PhUser class="size-3 shrink-0" weight="bold" />
            <span class="truncate">Awaiting assignment</span>
          </template>
        </div>
      </div>
      <PhCaretRight class="size-3.5 text-muted-foreground/40 shrink-0" weight="bold" />
    </div>
  </button>
</template>

<script lang="ts" setup>
import {
  PhCalendarDots,
  PhCaretRight,
  PhImage,
  PhStar,
  PhUser,
} from '@phosphor-icons/vue';
import { computed } from "vue";

import Avatar from "@/components/Avatar.vue";
import { formatSmartDateTime } from "@/lib/format";

export interface CustomerRequest {
  id: number;
  service_id: number;
  service_name: string | null;
  scheduled_time: string | null;
  address: string;
  pincode: string;
  service_status: string;
  remarks: string | null;
  date_of_request?: string | null;
  date_of_completion?: string | null;
  professional_id?: number | null;
  professional_name?: string | null;
}

export interface RelatedService {
  id: number;
  image_url?: string;
  category?: string | null;
  base_price?: number;
  time_required?: number;
  description?: string | null;
}

export interface RelatedProfessional {
  id: number;
  full_name: string;
  avatar_url?: string;
  rating?: number | null;
  review_count?: number | null;
  experience?: number | null;
}

const props = defineProps<{
  request: CustomerRequest;
  service?: RelatedService | null;
  professional?: RelatedProfessional | null;
}>();

defineEmits<{ open: [] }>();

const cancelled = computed(() => props.request.service_status === "cancelled");

const STATUS_STRIP: Record<string, { bg: string; label: string }> = {
  requested:   { bg: "bg-amber-500/90 text-white",    label: "Pending"   },
  accepted:    { bg: "bg-blue-500/90 text-white",     label: "Accepted"  },
  in_progress: { bg: "bg-blue-700/90 text-white",     label: "Active"    },
  completed:   { bg: "bg-emerald-600/90 text-white",  label: "Done"      },
  cancelled:   { bg: "bg-neutral-500/80 text-white",  label: "Cancelled" },
  rejected:    { bg: "bg-red-500/90 text-white",      label: "Rejected"  },
};

const strip = computed(() => STATUS_STRIP[props.request.service_status] ?? { bg: "bg-muted-foreground/50 text-white", label: props.request.service_status });
const statusStripClass = computed(() => strip.value.bg);
const statusLabel = computed(() => strip.value.label);
</script>
