<template>
  <div class="px-6 py-8 space-y-6">
    <AdminStatsCards
      :services-count="services.length"
      :professionals-count="professionals.length"
      :users-count="users.length"
      :pending-approvals="pendingApprovals"
    />
    <AdminAnalytics :data="analytics" />
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from "vue";

import { useAdminData } from "@/composables/useAdminData";
import { api } from "@/lib/api";
import { useNotificationsStore } from "@/stores/notifications";
import AdminAnalytics, {
  type AdminAnalyticsData,
  type ChartData,
} from "@/views/admin/AdminAnalytics.vue";
import AdminStatsCards from "@/views/admin/AdminStatsCards.vue";

interface AdminAnalyticsApi {
  request_trends?: { date: string; count: number }[];
  service_popularity?: { name: string; count: number }[];
  user_registrations?: { date: string; count: number }[];
  professional_status?: { status: string; count: number }[];
  user_status?: { status: string; count: number }[];
}

const EMPTY_ANALYTICS: AdminAnalyticsData = {
  requestTrends: null,
  servicePopularity: null,
  userRegistrations: null,
  professionalStatus: null,
  userStatus: null,
};

const { services, professionals, users, refreshAll } = useAdminData();
const toasts = useNotificationsStore();
const analytics = ref<AdminAnalyticsData>({ ...EMPTY_ANALYTICS });

const pendingApprovals = computed(
  () => professionals.value.filter((p) => p.approval_status === "pending").length,
);

onMounted(() => {
  refreshAll();
  fetchAnalytics();
});

async function fetchAnalytics() {
  try {
    const data = await api.get<AdminAnalyticsApi>("/api/analytics/admin");
    analytics.value = transformAnalytics(data);
  } catch (err) {
    console.error("analytics fetch failed", err);
    toasts.error("Failed to fetch analytics data");
  }
}

function transformAnalytics(data: AdminAnalyticsApi): AdminAnalyticsData {
  const fmtDate = (s: string) =>
    new Date(s).toLocaleString(undefined, { month: "short", day: "numeric" });
  const capitalize = (s: string) =>
    s.charAt(0).toUpperCase() + s.slice(1).replace("_", " ");

  const trendline = (
    rows: { date: string; count: number }[] | undefined,
    label: string,
    color: { border: string; bg: string },
  ): ChartData | null =>
    rows && rows.length
      ? {
          labels: rows.map((r) => fmtDate(r.date)),
          datasets: [
            {
              label,
              data: rows.map((r) => Math.round(r.count)),
              tension: 0.4,
              fill: true,
              backgroundColor: color.bg,
              borderColor: color.border,
            },
          ],
        }
      : null;

  return {
    requestTrends: trendline(data.request_trends, "Requests", {
      border: "#0043ce",
      bg: "rgba(0, 67, 206, 0.1)",
    }),
    servicePopularity:
      data.service_popularity && data.service_popularity.length
        ? {
            labels: data.service_popularity.map((s) => s.name),
            datasets: [
              {
                label: "Requests",
                data: data.service_popularity.map((s) => Math.round(s.count)),
                backgroundColor: "#4589ff",
              },
            ],
          }
        : null,
    userRegistrations: trendline(data.user_registrations, "Users", {
      border: "#198038",
      bg: "rgba(25, 128, 56, 0.1)",
    }),
    professionalStatus:
      data.professional_status && data.professional_status.length
        ? {
            labels: data.professional_status.map((p) => capitalize(p.status)),
            datasets: [
              {
                label: "Professionals",
                data: data.professional_status.map((p) => Math.round(p.count)),
                backgroundColor: ["#0043ce", "#4589ff", "#78a9ff"],
              },
            ],
          }
        : null,
    userStatus:
      data.user_status && data.user_status.length
        ? {
            labels: data.user_status.map((s) => s.status),
            datasets: [
              {
                label: "Users",
                data: data.user_status.map((s) => Math.round(s.count)),
                backgroundColor: ["#0043ce", "#da1e28"],
              },
            ],
          }
        : null,
  };
}
</script>
