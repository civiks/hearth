<script lang="ts" setup>
import { computed, onMounted, ref } from "vue";

import { DonutChart } from "@/components/charts";
import { categoricalPalette } from "@/components/charts/palette";
import { DashboardWidget, MetricStrip, type StripTile } from "@/components/dashboard";
import PageHeader from "@/components/PageHeader.vue";
import ProDigestCard from "@/components/genai/ProDigestCard.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { ApiError, api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import ApprovalNotice from "@/views/professional/ApprovalNotice.vue";
import type { ProRequest } from "@/views/professional/RequestsTable.vue";

interface ProRequestFull extends ProRequest {
  service_name?: string;
  date_of_request?: string;
}

interface Service {
  id: number;
  base_price: number;
}

interface ProAnalytics {
  completion_rate?: number;
  monthly_earnings?: { date: string; earnings: number }[];
  status_distribution?: { status: string; count: number }[];
}

const auth = useAuthStore();
const toasts = useNotificationsStore();

const requests = ref<ProRequestFull[]>([]);
const services = ref<Service[]>([]);
const analytics = ref<ProAnalytics>({});
const loaded = ref(false);

const pending = computed(() => requests.value.filter((r) => r.service_status === "requested"));
const inProgress = computed(() =>
  requests.value.filter((r) => r.service_status === "in_progress" || r.service_status === "accepted"),
);
const completed = computed(() => requests.value.filter((r) => r.service_status === "completed"));

const totalEarnings = computed(() =>
  completed.value.reduce((sum, r) => {
    const s = services.value.find((x) => x.id === r.service_id);
    return sum + (s ? s.base_price : 0);
  }, 0),
);

const earningsLabel = computed(() => {
  const v = totalEarnings.value;
  if (v >= 100_000) return `₹${(v / 100_000).toFixed(1)}L`;
  if (v >= 1_000) return `₹${(v / 1_000).toFixed(1)}k`;
  return `₹${v}`;
});

const stripTiles = computed<StripTile[]>(() => [
  { label: "Pending", value: pending.value.length, to: "/professional/requests" },
  { label: "In progress", value: inProgress.value.length, to: "/professional/requests" },
  { label: "Completed", value: completed.value.length, to: "/professional/requests" },
  { label: "Earnings", value: earningsLabel.value, to: "/professional/earnings" },
]);

const firstName = computed(() => auth.full_name?.split(" ")[0] ?? "");

const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 5) return "Hello";
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
});

const catColors = computed(() => categoricalPalette());

const statusLegend = computed(() =>
  (analytics.value.status_distribution ?? []).map((d, i) => ({
    label: capitalize(d.status),
    value: d.count,
    color: catColors.value[i % catColors.value.length],
  })),
);

const upNext = computed(() =>
  requests.value
    .filter((r) =>
      r.service_status === "requested" ||
      r.service_status === "accepted" ||
      r.service_status === "in_progress",
    )
    .sort((a, b) => (b.date_of_request ?? "").localeCompare(a.date_of_request ?? ""))
    .slice(0, 5),
);

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1).replace("_", " ");
}

onMounted(async () => {
  if (auth.approval_status !== "approved") return;
  try {
    const all = await api.get<ProRequestFull[]>("/api/requests");
    requests.value = all.filter((r) => r.service_id === auth.service_id);
    services.value = await api.get<Service[]>("/api/services");
    analytics.value = await api.get<ProAnalytics>("/api/analytics/professional");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to load data");
  } finally {
    loaded.value = true;
  }
});

</script>

<template>
  <div class="px-4 py-4 sm:px-6 sm:py-5 space-y-4 sm:space-y-6">
    <ApprovalNotice
      v-if="auth.approval_status === 'pending' || auth.approval_status === 'rejected'"
      :kind="auth.approval_status as 'pending' | 'rejected'"
    />

    <template v-if="auth.approval_status === 'approved'">
      <PageHeader
        :title="firstName ? `${greeting}, ${firstName}` : greeting"
        description="Here's how your service is doing today."
      />

      <ProDigestCard :requests="requests" :services="services" :loaded="loaded" />

      <MetricStrip title="This month" :tiles="stripTiles" />

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 items-stretch">
        <DashboardWidget
          title="Up next"
          :subtitle="`${pending.length + inProgress.length} active`"
          view-all-to="/professional/requests"
          body-class="h-44"
        >
          <ul v-if="upNext.length" class="divide-y">
            <li
              v-for="r in upNext"
              :key="r.id"
              class="flex items-center gap-3 py-1.5 text-sm"
            >
              <span class="flex-1 min-w-0 truncate">{{ r.customer_name ?? "—" }}</span>
              <StatusBadge :status="r.service_status" class="shrink-0" />
            </li>
          </ul>
          <p
            v-else
            class="h-full flex items-center justify-center text-xs text-muted-foreground"
          >
            Nothing active right now.
          </p>
        </DashboardWidget>

        <DashboardWidget
          title="Status breakdown"
          :subtitle="`${requests.length} total requests`"
          view-all-to="/professional/requests"
          body-class="h-44 pt-0 flex items-center gap-3"
          chart
        >
          <div v-if="statusLegend.length" class="size-32 shrink-0">
            <DonutChart
              :data="analytics.status_distribution ?? []"
              :value="(d) => d.count"
              :arc-width="6"
              :height="128"
            />
          </div>
          <ul v-if="statusLegend.length" class="flex-1 min-w-0 space-y-1.5 text-xs">
            <li
              v-for="item in statusLegend"
              :key="item.label"
              class="flex items-center gap-2"
            >
              <span class="block size-2 shrink-0" :style="{ background: item.color }" />
              <span class="text-muted-foreground truncate">{{ item.label }}</span>
              <span class="ml-auto font-medium tabular-nums">{{ item.value }}</span>
            </li>
          </ul>
          <p v-if="!statusLegend.length" class="text-xs text-muted-foreground">
            No data yet.
          </p>
        </DashboardWidget>
      </div>
    </template>
  </div>
</template>
