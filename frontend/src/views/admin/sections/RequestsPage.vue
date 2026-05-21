<template>
  <div class="px-6 py-8 min-w-0">
    <DataTable
      :columns="columns"
      :data="requests"
      title="All service requests"
      description="View every request on the platform."
      search-placeholder="Search requests"
      :global-filter-accessor="
        (r) => `${r.service_name ?? ''} ${r.customer_name ?? ''} ${r.pincode}`
      "
      empty-message="No service requests yet."
    />
  </div>
</template>

<script lang="ts" setup>
import { h, onMounted, ref } from "vue";
import type { ColumnDef } from "@tanstack/vue-table";

import StatusBadge from "@/components/StatusBadge.vue";
import { DataTable } from "@/components/ui/data-table";
import { api } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

interface AdminRequest {
  id: number;
  service_id: number;
  service_name: string | null;
  customer_id: number;
  customer_name: string | null;
  scheduled_time: string | null;
  service_status: string;
  pincode: string;
}

const requests = ref<AdminRequest[]>([]);

onMounted(async () => {
  try {
    requests.value = await api.get<AdminRequest[]>("/api/requests");
  } catch (err) {
    console.error("requests fetch failed", err);
  }
});

const columns: ColumnDef<AdminRequest>[] = [
  {
    accessorKey: "service_name",
    header: "Service",
    enableSorting: true,
    meta: { label: "Service", cellClass: "font-medium" },
    cell: ({ row }) => row.original.service_name ?? "—",
  },
  {
    accessorKey: "customer_name",
    header: "Customer",
    enableSorting: true,
    meta: { label: "Customer" },
    cell: ({ row }) => row.original.customer_name ?? "—",
  },
  {
    accessorKey: "scheduled_time",
    header: "Scheduled",
    enableSorting: true,
    meta: { label: "Scheduled", nowrap: true },
    cell: ({ row }) => formatDateTime(row.original.scheduled_time),
  },
  {
    id: "service_status",
    accessorKey: "service_status",
    header: "Status",
    enableSorting: true,
    filterFn: (row, _id, value: string[]) =>
      value.includes(row.original.service_status),
    meta: {
      label: "Status",
      filterOptions: [
        { label: "Requested", value: "requested" },
        { label: "Accepted", value: "accepted" },
        { label: "In progress", value: "in_progress" },
        { label: "Completed", value: "completed" },
        { label: "Cancelled", value: "cancelled" },
      ],
    },
    cell: ({ row }) => h(StatusBadge, { status: row.original.service_status }),
  },
  {
    accessorKey: "pincode",
    header: "Pincode",
    enableSorting: true,
    meta: { label: "Pincode", nowrap: true },
  },
];
</script>
