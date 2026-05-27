<script lang="ts" setup>
import { h, onMounted, ref } from "vue";
import type { ColumnDef } from "@tanstack/vue-table";

import { DataTable } from "@/components/ui/data-table";
import { ApiError, api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import ApprovalNotice from "@/views/professional/ApprovalNotice.vue";

interface ProRequestRaw {
  id: number;
  service_id: number;
  customer_name: string | null;
  service_status: string;
  scheduled_time: string | null;
  date_of_completion?: string | null;
  date_of_request?: string;
}

interface Service {
  id: number;
  name: string;
  base_price: number;
}

interface EarningRow {
  id: number;
  date: string | null;
  customer_name: string;
  service_name: string;
  amount: number;
}

const auth = useAuthStore();
const toasts = useNotificationsStore();

const earnings = ref<EarningRow[]>([]);
const loading = ref(false);

onMounted(async () => {
  if (auth.approval_status !== "approved") return;
  loading.value = true;
  try {
    const [reqs, svcs] = await Promise.all([
      api.get<ProRequestRaw[]>("/api/requests"),
      api.get<Service[]>("/api/services"),
    ]);
    const mine = reqs.filter(
      (r) => r.service_id === auth.service_id && r.service_status === "completed",
    );
    earnings.value = mine
      .map((r) => {
        const svc = svcs.find((s) => s.id === r.service_id);
        return {
          id: r.id,
          date: r.date_of_completion ?? r.date_of_request ?? null,
          customer_name: r.customer_name ?? "—",
          service_name: svc?.name ?? "—",
          amount: svc?.base_price ?? 0,
        };
      })
      .sort((a, b) => (b.date ?? "").localeCompare(a.date ?? ""));
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to load earnings");
  } finally {
    loading.value = false;
  }
});

function inrLong(v: number): string {
  return `₹${Math.round(v).toLocaleString("en-IN")}`;
}

function asLongDate(s: string | null): string {
  if (!s) return "—";
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return s;
  return d.toLocaleString(undefined, { day: "2-digit", month: "short", year: "numeric" });
}

const columns: ColumnDef<EarningRow>[] = [
  {
    accessorKey: "date",
    header: "Completed",
    enableSorting: true,
    sortingFn: (a, b) => (a.original.date ?? "").localeCompare(b.original.date ?? ""),
    meta: { label: "Completed", nowrap: true },
    cell: ({ row }) => asLongDate(row.original.date),
  },
  {
    accessorKey: "customer_name",
    header: "Customer",
    enableSorting: true,
    meta: { label: "Customer" },
    cell: ({ row }) =>
      h("span", { class: "text-sm" }, row.original.customer_name),
  },
  {
    accessorKey: "service_name",
    header: "Service",
    enableSorting: true,
    meta: { label: "Service" },
  },
  {
    accessorKey: "amount",
    header: "Amount",
    enableSorting: true,
    meta: { label: "Amount", align: "right", nowrap: true, cellClass: "tabular-nums" },
    cell: ({ row }) => inrLong(row.original.amount),
  },
];
</script>

<template>
  <div class="px-4 py-4 sm:px-6 sm:py-8 space-y-6">
    <ApprovalNotice
      v-if="auth.approval_status === 'pending' || auth.approval_status === 'rejected'"
      :kind="auth.approval_status as 'pending' | 'rejected'"
    />

    <template v-if="auth.approval_status === 'approved'">
      <DataTable
        :columns="columns"
        :data="earnings"
        :loading="loading"
        title="Payouts"
        description="One row per completed booking, most recent first."
        search-placeholder="Search by customer or service"
        :global-filter-accessor="(r) => `${r.customer_name} ${r.service_name}`"
        empty-message="No completed bookings yet."
      />
    </template>
  </div>
</template>
