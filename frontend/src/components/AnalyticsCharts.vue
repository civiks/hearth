<template>
  <div ref="root" style="width: 100%; height: 100%;"></div>
</template>

<script lang="ts">
import {
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  DoughnutController,
  Filler,
  Legend,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";
import { defineComponent, type PropType } from "vue";

Chart.register(
  BarController,
  BarElement,
  LineController,
  LineElement,
  PointElement,
  DoughnutController,
  ArcElement,
  CategoryScale,
  LinearScale,
  Filler,
  Legend,
  Title,
  Tooltip,
);

export type ChartType = "line" | "bar" | "doughnut";

interface ChartDataset {
  label: string;
  data: number[];
  [key: string]: unknown;
}

interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export default defineComponent({
  name: "AnalyticsCharts",
  props: {
    chartType: { type: String as PropType<ChartType>, required: true },
    chartData: { type: Object as PropType<ChartData>, required: true },
    title: { type: String, default: "" },
  },
  data() {
    return {
      // Chart's generics blow up TS inference here; treat as opaque.
      chart: null as unknown,
    };
  },
  watch: {
    chartData: {
      deep: true,
      handler() {
        this.destroyChart();
        this.createChart();
      },
    },
  },
  mounted() {
    this.createChart();
  },
  beforeUnmount() {
    this.destroyChart();
  },
  methods: {
    createChart() {
      const root = this.$refs.root as HTMLElement;
      const canvas = document.createElement("canvas");
      root.appendChild(canvas);

      const isEarnings =
        this.chartType === "line" &&
        (this.chartData.datasets[0]?.label ?? "").includes("Earnings");

      const options: Record<string, unknown> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, position: "bottom" },
          title: { display: !!this.title, text: this.title },
        },
      };

      if (this.chartType !== "doughnut") {
        options.scales = {
          y: {
            beginAtZero: true,
            ticks: { precision: 0, stepSize: isEarnings ? 100 : 1 },
          },
        };
      }

      this.chart = new Chart(canvas, {
        type: this.chartType,
        data: {
          labels: this.chartData.labels,
          datasets: this.chartData.datasets.map((d) => ({
            ...d,
            data: d.data.map((v) => Math.round(v)),
          })),
        },
        options,
      });
    },
    destroyChart() {
      if (this.chart) {
        (this.chart as Chart).destroy();
        this.chart = null;
      }
      const root = this.$refs.root as HTMLElement | undefined;
      if (root) root.innerHTML = "";
    },
  },
});
</script>
