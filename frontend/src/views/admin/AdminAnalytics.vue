<template>
  <section class="space-y-4">
    <ChartCard
      title="Service request trends"
      :has-data="!!data.requestTrends"
      :height="300"
    >
      <AnalyticsCharts
        v-if="data.requestTrends"
        chart-type="line"
        :chart-data="data.requestTrends"
      />
    </ChartCard>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <ChartCard
        title="Service popularity"
        :has-data="!!data.servicePopularity"
        :height="300"
      >
        <AnalyticsCharts
          v-if="data.servicePopularity"
          chart-type="bar"
          :chart-data="data.servicePopularity"
        />
      </ChartCard>
      <ChartCard
        title="User registration trends"
        :has-data="!!data.userRegistrations"
        :height="300"
      >
        <AnalyticsCharts
          v-if="data.userRegistrations"
          chart-type="line"
          :chart-data="data.userRegistrations"
        />
      </ChartCard>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <ChartCard
        title="Professional status"
        :has-data="!!data.professionalStatus"
        :height="300"
        :empty-icon="PieChart"
      >
        <AnalyticsCharts
          v-if="data.professionalStatus"
          chart-type="doughnut"
          :chart-data="data.professionalStatus"
        />
      </ChartCard>
      <ChartCard
        title="User status"
        :has-data="!!data.userStatus"
        :height="300"
        :empty-icon="PieChart"
      >
        <AnalyticsCharts
          v-if="data.userStatus"
          chart-type="doughnut"
          :chart-data="data.userStatus"
        />
      </ChartCard>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { PieChart } from "lucide-vue-next";

import AnalyticsCharts from "@/components/AnalyticsCharts.vue";
import ChartCard from "@/components/ChartCard.vue";

export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string;
    tension?: number;
    fill?: boolean;
  }>;
}

export interface AdminAnalyticsData {
  requestTrends: ChartData | null;
  servicePopularity: ChartData | null;
  userRegistrations: ChartData | null;
  professionalStatus: ChartData | null;
  userStatus: ChartData | null;
}

defineProps<{ data: AdminAnalyticsData }>();
</script>
