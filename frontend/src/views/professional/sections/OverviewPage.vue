<template>
  <div class="px-6 py-8 space-y-6">
    <ApprovalNotice
      v-if="auth.approval_status === 'pending' || auth.approval_status === 'rejected'"
      :kind="auth.approval_status as 'pending' | 'rejected'"
    />

    <template v-if="auth.approval_status === 'approved'">
      <!-- Profile header (richer in demo mode where avatar/rating exist) -->
      <article
        v-if="profile"
        class="bg-card p-5 flex flex-col md:flex-row items-start md:items-center gap-4"
      >
        <ProfessionalAvatar
          :name="profile.full_name"
          :src="profile.avatar_url"
          class="size-16 shrink-0"
        />
        <div class="flex-1 min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <h1 class="text-lg font-medium">{{ profile.full_name }}</h1>
            <Badge variant="secondary" v-if="profile.service_name">
              {{ profile.service_name }}
            </Badge>
          </div>
          <p
            v-if="profile.description"
            class="text-sm text-muted-foreground mt-1 max-w-prose"
          >
            {{ profile.description }}
          </p>
          <div class="flex flex-wrap items-center gap-4 text-xs text-muted-foreground mt-2">
            <span v-if="profile.rating != null" class="inline-flex items-center gap-1">
              <Star class="size-3.5 fill-amber-400 text-amber-400" />
              <span class="text-foreground font-medium">
                {{ profile.rating.toFixed(1) }}
              </span>
              <span v-if="profile.review_count != null">
                ({{ profile.review_count }} reviews)
              </span>
            </span>
            <span v-if="profile.experience != null">
              {{ profile.experience }} years experience
            </span>
            <span v-if="profile.pincode">PIN {{ profile.pincode }}</span>
          </div>
        </div>
      </article>

      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Pending" :value="pending.length" />
        <StatCard label="In progress" :value="inProgress.length" />
        <StatCard label="Completed" :value="completed.length" />
        <StatCard label="Earnings" :value="`₹${totalEarnings}`" />
      </div>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { Star } from "lucide-vue-next";
import { computed, onMounted, ref } from "vue";

import ProfessionalAvatar from "@/components/marketplace/ProfessionalAvatar.vue";
import StatCard from "@/components/StatCard.vue";
import { Badge } from "@/components/ui/badge";
import { ApiError, api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import ApprovalNotice from "@/views/professional/ApprovalNotice.vue";
import type { ProRequest } from "@/views/professional/RequestsTable.vue";

interface Service {
  id: number;
  base_price: number;
}

interface ProfileMe {
  full_name: string;
  service_name?: string | null;
  description?: string | null;
  pincode?: string | null;
  experience?: number | null;
  avatar_url?: string;
  rating?: number | null;
  review_count?: number | null;
}

const auth = useAuthStore();
const toasts = useNotificationsStore();

const requests = ref<ProRequest[]>([]);
const services = ref<Service[]>([]);
const profile = ref<ProfileMe | null>(null);

const pending = computed(() => requests.value.filter((r) => r.service_status === "requested"));
const inProgress = computed(() => requests.value.filter((r) => r.service_status === "in_progress"));
const completed = computed(() => requests.value.filter((r) => r.service_status === "completed"));

const totalEarnings = computed(() =>
  completed.value.reduce((sum, r) => {
    const s = services.value.find((x) => x.id === r.service_id);
    return sum + (s ? s.base_price : 0);
  }, 0),
);

onMounted(async () => {
  if (auth.approval_status !== "approved") return;
  try {
    const all = await api.get<ProRequest[]>("/api/requests");
    requests.value = all.filter((r) => r.service_id === auth.service_id);
    services.value = await api.get<Service[]>("/api/services");
    profile.value = await api.get<ProfileMe>("/api/users/me");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to load data");
  }
});
</script>
