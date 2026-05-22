<script lang="ts" setup>
import { computed, onMounted, ref } from "vue";

import { DonutChart } from "@/components/charts";
import { categoricalPalette } from "@/components/charts/palette";
import { DashboardWidget, StatWidget } from "@/components/dashboard";
import { useAdminData } from "@/composables/useAdminData";
import { api } from "@/lib/api";
import { useNotificationsStore } from "@/stores/notifications";

interface TrendPoint { date: string; count: number }
interface StatusSlice { status: string; count: number }
interface ServicePoint { name: string; count: number }
interface AdminAnalyticsApi {
  request_trends?: TrendPoint[];
  service_popularity?: ServicePoint[];
  user_registrations?: TrendPoint[];
  professional_status?: StatusSlice[];
  user_status?: StatusSlice[];
}

const { professionals, users, refreshAll } = useAdminData();
const toasts = useNotificationsStore();
const analytics = ref<AdminAnalyticsApi>({});

onMounted(async () => {
  await refreshAll();
  try {
    analytics.value = await api.get<AdminAnalyticsApi>("/api/analytics/admin");
  } catch (err) {
    console.error("analytics fetch failed", err);
    toasts.error("Failed to fetch analytics data");
  }
});

function half(points: TrendPoint[] | undefined): { sparkline: number[]; delta: number | undefined } {
  if (!points || points.length < 2) return { sparkline: [], delta: undefined };
  const sparkline = points.map((p) => p.count);
  const mid = Math.floor(points.length / 2);
  const earlier = points.slice(0, mid).reduce((s, p) => s + p.count, 0);
  const latest = points.slice(mid).reduce((s, p) => s + p.count, 0);
  if (earlier === 0) return { sparkline, delta: undefined };
  return { sparkline, delta: (latest - earlier) / earlier };
}

const requestStats = computed(() => half(analytics.value.request_trends));
const userStats = computed(() => half(analytics.value.user_registrations));

const totalRequests = computed(
  () => analytics.value.request_trends?.reduce((s, p) => s + p.count, 0) ?? 0,
);

const topServices = computed(() => (analytics.value.service_popularity ?? []).slice(0, 5));

const proStatusTotal = computed(
  () => analytics.value.professional_status?.reduce((s, p) => s + p.count, 0) ?? 0,
);
const userStatusTotal = computed(
  () => analytics.value.user_status?.reduce((s, p) => s + p.count, 0) ?? 0,
);

const catColors = computed(() => categoricalPalette());

const proStatusLegend = computed(() =>
  (analytics.value.professional_status ?? []).map((d, i) => ({
    label: capitalize(d.status),
    value: d.count,
    color: catColors.value[i % catColors.value.length],
  })),
);
const userStatusLegend = computed(() =>
  (analytics.value.user_status ?? []).map((d, i) => ({
    label: capitalize(d.status),
    value: d.count,
    color: catColors.value[i % catColors.value.length],
  })),
);

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1).replace("_", " ");
}

</script>

<template>
  <div class="px-6 py-8">
    <header class="mb-6">
      <h1 class="text-2xl font-light tracking-tight">Overview</h1>
      <p class="mt-1 text-sm text-muted-foreground">
        Activity across the platform at a glance.
      </p>
    </header>

    <div class="grid grid-cols-1 sm:grid-cols-12 gap-4 items-stretch">
      <StatWidget
        class="sm:col-span-4"
        title="Service requests"
        :value="totalRequests"
        :delta="requestStats.delta"
        :trend="requestStats.sparkline"
        to="/admin/requests"
      />
      <StatWidget
        class="sm:col-span-4"
        title="Registered users"
        :value="users.length"
        :delta="userStats.delta"
        :trend="userStats.sparkline"
        to="/admin/users"
      />
      <StatWidget
        class="sm:col-span-4"
        title="Active professionals"
        :value="professionals.length"
        to="/admin/professionals"
      />

      <DashboardWidget
        class="sm:col-span-4"
        title="Top services"
        subtitle="By bookings"
        view-all-to="/admin/services"
        body-class="h-44"
      >
        <ul v-if="topServices.length" class="divide-y">
          <li
            v-for="s in topServices"
            :key="s.name"
            class="flex items-center gap-3 py-1.5 text-sm"
          >
            <span class="flex-1 min-w-0 truncate">{{ s.name }}</span>
            <span class="text-muted-foreground tabular-nums">{{ s.count }}</span>
          </li>
        </ul>
        <p v-else class="text-xs text-muted-foreground">No data yet.</p>
      </DashboardWidget>

      <DashboardWidget
        class="sm:col-span-4"
        title="Professional status"
        :subtitle="`${proStatusTotal} total`"
        view-all-to="/admin/professionals"
        body-class="h-44 pt-0 flex items-center gap-3"
        chart
      >
        <div v-if="proStatusLegend.length" class="size-32 shrink-0">
          <DonutChart
            :data="analytics.professional_status ?? []"
            :value="(d) => d.count"
            :arc-width="6"
            :height="128"
          />
        </div>
        <ul v-if="proStatusLegend.length" class="flex-1 min-w-0 space-y-1.5 text-xs">
          <li
            v-for="item in proStatusLegend"
            :key="item.label"
            class="flex items-center gap-2"
          >
            <span class="block size-2 shrink-0" :style="{ background: item.color }" />
            <span class="text-muted-foreground truncate">{{ item.label }}</span>
            <span class="ml-auto font-medium tabular-nums">{{ item.value }}</span>
          </li>
        </ul>
        <p v-if="!proStatusLegend.length" class="text-xs text-muted-foreground">
          No data yet.
        </p>
      </DashboardWidget>

      <DashboardWidget
        class="sm:col-span-4"
        title="User status"
        :subtitle="`${userStatusTotal} total`"
        view-all-to="/admin/users"
        body-class="h-44 pt-0 flex items-center gap-3"
        chart
      >
        <div v-if="userStatusLegend.length" class="size-32 shrink-0">
          <DonutChart
            :data="analytics.user_status ?? []"
            :value="(d) => d.count"
            :arc-width="6"
            :height="128"
          />
        </div>
        <ul v-if="userStatusLegend.length" class="flex-1 min-w-0 space-y-1.5 text-xs">
          <li
            v-for="item in userStatusLegend"
            :key="item.label"
            class="flex items-center gap-2"
          >
            <span class="block size-2 shrink-0" :style="{ background: item.color }" />
            <span class="text-muted-foreground truncate">{{ item.label }}</span>
            <span class="ml-auto font-medium tabular-nums">{{ item.value }}</span>
          </li>
        </ul>
        <p v-if="!userStatusLegend.length" class="text-xs text-muted-foreground">
          No data yet.
        </p>
      </DashboardWidget>
    </div>
  </div>
</template>
