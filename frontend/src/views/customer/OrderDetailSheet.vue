<template>
  <ResponsiveSheet
    :open="true"
    body-class="space-y-6"
    @close="$emit('close')"
  >
    <template #header>
      <div :class="isDesktop ? 'flex flex-col gap-1.5 px-5 pt-5 pb-4 border-b' : 'flex flex-col gap-1.5 px-5 pt-3'">
        <p class="text-2xl font-semibold tracking-tight tabular-nums">
          {{ request.scheduled_time ? formatSmartDateTime(request.scheduled_time) : `Order #${request.id}` }}
        </p>
        <component :is="isDesktop ? SheetTitle : DrawerTitle" class="text-sm font-medium tracking-tight">
          {{ request.service_name }}<template v-if="service?.category"><span class="font-normal text-muted-foreground"> · {{ service.category }}</span></template>
        </component>
      </div>
    </template>

    <!-- Status -->
    <StatusTimeline :status="request.service_status" />

    <!-- Professional -->
    <div class="border-t pt-5">
      <div v-if="professional" class="flex items-center gap-3">
        <ProfessionalAvatar
          :name="professional.full_name"
          :src="professional.avatar_url"
          class="size-9 shrink-0"
        />
        <div class="min-w-0">
          <p class="text-sm font-medium tracking-tight">{{ professional.full_name }}</p>
          <p class="text-xs tracking-tight tabular-nums text-muted-foreground mt-0.5">
            <template v-if="professional.rating != null">
              <PhStar weight="fill" class="size-3 text-amber-400 inline-block -mt-px" />
              {{ professional.rating.toFixed(1) }}
              <template v-if="professional.review_count"> ({{ professional.review_count }})</template>
            </template>
            <template v-if="professional.experience">
              <span v-if="professional.rating != null"> · </span>
              {{ professional.experience }} yrs experience
            </template>
          </p>
        </div>
      </div>
      <p v-else-if="!cancelled" class="text-sm text-muted-foreground">
        Awaiting professional assignment
      </p>
      <p v-else class="text-sm text-muted-foreground">No professional assigned</p>
    </div>

    <!-- Details -->
    <div class="border-t pt-5 space-y-3 text-sm tracking-tight">
      <div class="flex items-start gap-2.5">
        <PhMapPin class="size-4 shrink-0 mt-0.5 text-muted-foreground" />
        <span>{{ request.address }}, <span class="tabular-nums">{{ request.pincode }}</span></span>
      </div>
      <div v-if="service?.base_price != null || service?.time_required != null" class="flex items-center gap-2.5">
        <PhTag class="size-4 shrink-0 text-muted-foreground" />
        <span class="flex items-baseline gap-1.5 tabular-nums">
          <span v-if="service?.base_price != null" class="inline-flex items-end gap-0.5 font-medium">
            <span class="text-[11px] leading-none text-muted-foreground mb-px">Rs</span>
            <span class="leading-none">{{ service!.base_price }}</span>
          </span>
          <span v-if="service?.base_price != null && service?.time_required != null" class="text-muted-foreground">·</span>
          <span v-if="service?.time_required != null">{{ service!.time_required }} min</span>
        </span>
      </div>
      <p v-if="request.date_of_request" class="text-xs tracking-tight tabular-nums text-muted-foreground pl-[26px]">
        Ordered {{ formatSmartDate(request.date_of_request) }}
      </p>
    </div>

    <!-- Notes -->
    <div v-if="request.remarks" class="border-t pt-5">
      <p class="text-[11px] font-medium uppercase tracking-wide text-muted-foreground mb-2">Notes</p>
      <p class="text-sm tracking-tight leading-relaxed">{{ request.remarks }}</p>
    </div>

    <template v-if="isActionable" #footer>
      <Button
        v-if="request.service_status === 'requested'"
        variant="outline"
        class="flex-1"
        @click="onEdit"
      >
        Edit booking
      </Button>
      <Button variant="destructive-soft" class="flex-1" @click="onCancel">
        Cancel request
      </Button>
    </template>
  </ResponsiveSheet>
</template>

<script lang="ts" setup>
import {
  PhMapPin,
  PhStar,
  PhTag,
} from '@phosphor-icons/vue';
import { computed } from "vue";
import { useMediaQuery } from "@vueuse/core";

import ProfessionalAvatar from "@/components/marketplace/ProfessionalAvatar.vue";
import StatusTimeline from "@/components/marketplace/StatusTimeline.vue";
import { Button } from "@/components/ui/button";
import { DrawerTitle } from "@/components/ui/drawer";
import ResponsiveSheet from "@/components/ui/ResponsiveSheet.vue";
import { SheetTitle } from "@/components/ui/sheet";
import { formatSmartDate, formatSmartDateTime } from "@/lib/format";
import type { CustomerRequest, RelatedProfessional, RelatedService } from "./RequestCard.vue";

const props = defineProps<{
  request: CustomerRequest;
  service?: RelatedService | null;
  professional?: RelatedProfessional | null;
}>();

const emit = defineEmits<{ close: []; edit: []; cancel: [] }>();

const isDesktop = useMediaQuery("(min-width: 640px)");

const cancelled = computed(() => props.request.service_status === "cancelled");
const isActionable = computed(() =>
  ["requested", "accepted"].includes(props.request.service_status),
);

function onEdit() {
  emit("edit");
  emit("close");
}

function onCancel() {
  emit("cancel");
  emit("close");
}
</script>
