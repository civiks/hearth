<template>
  <div class="px-6 py-8 space-y-6">
    <ApprovalNotice
      v-if="auth.approval_status === 'pending' || auth.approval_status === 'rejected'"
      :kind="auth.approval_status as 'pending' | 'rejected'"
    />
    <ProfessionalAnalytics v-else :data="analytics" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from "vue";

import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import ApprovalNotice from "@/views/professional/ApprovalNotice.vue";
import ProfessionalAnalytics, {
  type ProfessionalAnalyticsData,
} from "@/views/professional/ProfessionalAnalytics.vue";
import type { ChartData } from "@/views/admin/AdminAnalytics.vue";

interface AnalyticsApi {
  completion_rate: number;
  monthly_earnings: { date: string; earnings: number }[];
  status_distribution: { status: string; count: number }[];
}

const EMPTY_ANALYTICS: ProfessionalAnalyticsData = {
  monthlyEarnings: null,
  completionRate: null,
  statusDistribution: null,
};

const auth = useAuthStore();
const toasts = useNotificationsStore();
const analytics = ref<ProfessionalAnalyticsData>({ ...EMPTY_ANALYTICS });

onMounted(async () => {
  if (auth.approval_status !== "approved") return;
  try {
    const data = await api.get<AnalyticsApi>("/api/analytics/professional");
    analytics.value = transformAnalytics(data);
  } catch (err) {
    console.error(err);
    toasts.error("Failed to fetch analytics");
  }
});

function transformAnalytics(data: AnalyticsApi): ProfessionalAnalyticsData {
  const rate = data.completion_rate || 0;
  const completionRate: ChartData = {
    labels: ["Completed", "Remaining"],
    datasets: [
      {
        label: "Service Completion Rate",
        data: [Number(rate.toFixed(1)), Number((100 - rate).toFixed(1))],
        backgroundColor: ["#0043ce", "#4589ff"],
      },
    ],
  };

  const monthlyEarnings: ChartData | null = data.monthly_earnings.length
    ? {
        labels: data.monthly_earnings.map((e) =>
          new Date(e.date).toLocaleString(undefined, { month: "short", year: "numeric" }),
        ),
        datasets: [
          {
            label: "Monthly Earnings (₹)",
            data: data.monthly_earnings.map((e) => Math.round(e.earnings)),
            borderColor: "#0043ce",
            tension: 0.4,
            fill: true,
            backgroundColor: "rgba(0, 67, 206, 0.1)",
          },
        ],
      }
    : null;

  const statusDistribution: ChartData | null = data.status_distribution.length
    ? {
        labels: data.status_distribution.map(
          (s) => s.status.charAt(0).toUpperCase() + s.status.slice(1).replace("_", " "),
        ),
        datasets: [
          {
            label: "Request Status Distribution",
            data: data.status_distribution.map((s) => Math.round(s.count)),
            backgroundColor: ["#0043ce", "#4589ff", "#78a9ff", "#a6c8ff"],
          },
        ],
      }
    : null;

  return { monthlyEarnings, completionRate, statusDistribution };
}
</script>
