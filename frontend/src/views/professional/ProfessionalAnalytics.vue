<template>
  <section class="space-y-4">
    <ChartCard
      title="Monthly earnings"
      :has-data="!!data.monthlyEarnings"
      :height="300"
    >
      <AnalyticsCharts
        v-if="data.monthlyEarnings"
        chart-type="line"
        :chart-data="data.monthlyEarnings"
      />
    </ChartCard>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <ChartCard
        title="Completion rate"
        :has-data="!!data.completionRate"
        :height="300"
        :empty-icon="PieChart"
      >
        <AnalyticsCharts
          v-if="data.completionRate"
          chart-type="doughnut"
          :chart-data="data.completionRate"
        />
      </ChartCard>
      <ChartCard
        title="Request status"
        :has-data="!!data.statusDistribution"
        :height="300"
      >
        <AnalyticsCharts
          v-if="data.statusDistribution"
          chart-type="bar"
          :chart-data="data.statusDistribution"
        />
      </ChartCard>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { PieChart } from "lucide-vue-next";

import AnalyticsCharts from "@/components/AnalyticsCharts.vue";
import ChartCard from "@/components/ChartCard.vue";
import type { ChartData } from "@/views/admin/AdminAnalytics.vue";

export interface ProfessionalAnalyticsData {
  monthlyEarnings: ChartData | null;
  completionRate: ChartData | null;
  statusDistribution: ChartData | null;
}

defineProps<{ data: ProfessionalAnalyticsData }>();
</script>
