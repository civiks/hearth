<template>
  <article
    class="bg-card rounded-lg soft-card card-lift overflow-hidden flex flex-col md:flex-row"
    :class="cancelled ? 'opacity-70' : ''"
  >
    <!-- Service photo strip -->
    <div class="md:w-48 shrink-0 bg-muted">
      <img
        v-if="service?.image_url"
        :src="service.image_url"
        :alt="request.service_name ?? 'Service'"
        loading="lazy"
        class="size-full object-cover aspect-[4/3] md:aspect-auto"
      />
      <div
        v-else
        class="size-full flex items-center justify-center aspect-[4/3] md:aspect-auto"
      >
        <Image class="size-8 text-muted-foreground/60" />
      </div>
    </div>

    <!-- Body -->
    <div class="flex-1 p-4 space-y-3">
      <div class="flex items-start justify-between gap-3">
        <div>
          <Badge v-if="service?.category" variant="secondary" class="mb-1">
            {{ service.category }}
          </Badge>
          <h3 class="text-base font-medium">{{ request.service_name }}</h3>
          <div class="flex items-center gap-3 text-xs text-muted-foreground mt-1">
            <span class="inline-flex items-center gap-1">
              <Calendar class="size-3" />
              {{ formatDateTime(request.scheduled_time) }}
            </span>
            <span class="inline-flex items-center gap-1">
              <MapPin class="size-3" />
              {{ request.address }}, {{ request.pincode }}
            </span>
          </div>
        </div>

        <DropdownMenu v-if="isActionable">
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" size="icon" aria-label="Open menu">
              <MoreVertical class="size-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              v-if="request.service_status === 'requested'"
              @click="$emit('edit')"
            >
              <Edit2 class="mr-2 size-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              variant="destructive"
              @click="$emit('cancel')"
            >
              <XCircle class="mr-2 size-4" />
              Cancel
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <!-- Professional info -->
      <div v-if="professional" class="flex items-center gap-3 border-t pt-3">
        <ProfessionalAvatar
          :name="professional.full_name"
          :src="professional.avatar_url"
          class="size-9 shrink-0"
        />
        <div class="flex-1 min-w-0">
          <div class="text-sm font-medium truncate">{{ professional.full_name }}</div>
          <div class="text-xs text-muted-foreground flex items-center gap-2">
            <span v-if="professional.rating != null" class="inline-flex items-center gap-1">
              <Star class="size-3 fill-amber-400 text-amber-400" />
              {{ professional.rating.toFixed(1) }}
              <span v-if="professional.review_count">
                ({{ professional.review_count }})
              </span>
            </span>
            <span v-if="professional.experience">
              {{ professional.experience }} yrs experience
            </span>
          </div>
        </div>
      </div>

      <div v-else-if="!cancelled" class="text-xs text-muted-foreground border-t pt-3">
        Awaiting professional assignment…
      </div>

      <!-- Status timeline -->
      <div class="border-t pt-3">
        <StatusTimeline :status="request.service_status" />
      </div>

      <p v-if="request.remarks" class="text-xs text-muted-foreground border-t pt-3">
        <span class="font-medium">Note:</span> {{ request.remarks }}
      </p>
    </div>
  </article>
</template>

<script lang="ts" setup>
import {
  Calendar,
  Edit2,
  Image,
  MapPin,
  MoreVertical,
  Star,
  XCircle,
} from "lucide-vue-next";
import { computed } from "vue";

import ProfessionalAvatar from "@/components/marketplace/ProfessionalAvatar.vue";
import StatusTimeline from "@/components/marketplace/StatusTimeline.vue";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { formatDateTime } from "@/lib/format";

export interface CustomerRequest {
  id: number;
  service_id: number;
  service_name: string | null;
  scheduled_time: string | null;
  address: string;
  pincode: string;
  service_status: string;
  remarks: string | null;
  professional_id?: number | null;
  professional_name?: string | null;
}

export interface RelatedService {
  id: number;
  image_url?: string;
  category?: string | null;
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

defineEmits<{ edit: []; cancel: [] }>();

const cancelled = computed(() => props.request.service_status === "cancelled");
const isActionable = computed(() =>
  ["requested", "accepted"].includes(props.request.service_status),
);
</script>
