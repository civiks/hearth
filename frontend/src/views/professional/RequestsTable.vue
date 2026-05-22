<template>
  <DataTable
    :columns="columns"
    :data="requests"
    title="Service requests"
    description="Active and historical bookings assigned to you."
    search-placeholder="Search requests"
    :global-filter-accessor="
      (r) => `${r.customer_name ?? ''} ${r.address} ${r.pincode} ${r.remarks ?? ''}`
    "
    empty-message="No requests match your filters."
  />
</template>

<script lang="ts" setup>
import {
  CheckCircle,
  MoreVertical,
  PlayCircle,
} from "lucide-vue-next";
import { h } from "vue";
import type { ColumnDef } from "@tanstack/vue-table";

import UserAvatar, { type AvatarVariant } from "@/components/Avatar.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { formatDateTime } from "@/lib/format";

export interface ProRequest {
  id: number;
  service_id: number;
  customer_name: string | null;
  address: string;
  pincode: string;
  scheduled_time: string | null;
  service_status: string;
  remarks: string | null;
}

const props = defineProps<{ requests: ProRequest[] }>();
const emit = defineEmits<{ updateStatus: [id: number, status: string] }>();
void props;

function avatarVariant(r: ProRequest): AvatarVariant {
  switch (r.service_status) {
    case "requested":
      return "warning";
    case "accepted":
      return "primary";
    case "in_progress":
      return "info";
    case "completed":
      return "success";
    case "cancelled":
      return "danger";
    default:
      return "primary";
  }
}

const columns: ColumnDef<ProRequest>[] = [
  {
    accessorKey: "customer_name",
    header: "Customer",
    enableSorting: true,
    meta: { label: "Customer" },
    cell: ({ row }) => {
      const r = row.original;
      return h(
        "div",
        { class: "flex items-center gap-3 min-w-0" },
        [
          h(UserAvatar, {
            name: r.customer_name ?? "",
            variant: avatarVariant(r),
          }),
          h(
            "div",
            { class: "leading-tight min-w-0" },
            [
              h(
                "div",
                { class: "text-sm font-medium truncate" },
                r.customer_name ?? "—",
              ),
              h(
                "div",
                { class: "text-xs text-muted-foreground truncate" },
                r.address,
              ),
              h(
                "div",
                { class: "text-xs text-muted-foreground" },
                r.pincode,
              ),
            ],
          ),
        ],
      );
    },
  },
  {
    accessorKey: "remarks",
    header: "Remarks",
    enableSorting: false,
    meta: { label: "Remarks", cellClass: "text-muted-foreground max-w-xs" },
    cell: ({ row }) => row.original.remarks || "No remarks",
  },
  {
    accessorKey: "scheduled_time",
    header: "Schedule",
    enableSorting: true,
    meta: { label: "Schedule", nowrap: true },
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
    id: "actions",
    header: "",
    enableSorting: false,
    enableHiding: false,
    meta: { align: "right" },
    cell: ({ row }) => {
      const r = row.original;
      const items: ReturnType<typeof h>[] = [];

      if (r.service_status === "requested") {
        items.push(
          h(
            DropdownMenuItem,
            { onClick: () => emit("updateStatus", r.id, "accepted") },
            {
              default: () => [
                h(CheckCircle, { class: "mr-2 size-4" }),
                "Accept request",
              ],
            },
          ),
        );
      } else if (r.service_status === "accepted") {
        items.push(
          h(
            DropdownMenuItem,
            { onClick: () => emit("updateStatus", r.id, "in_progress") },
            {
              default: () => [
                h(PlayCircle, { class: "mr-2 size-4" }),
                "Start work",
              ],
            },
          ),
        );
      } else if (r.service_status === "in_progress") {
        items.push(
          h(
            DropdownMenuItem,
            { onClick: () => emit("updateStatus", r.id, "completed") },
            {
              default: () => [
                h(CheckCircle, { class: "mr-2 size-4" }),
                "Mark as complete",
              ],
            },
          ),
        );
      }

      if (items.length === 0) return null;

      return h(DropdownMenu, null, {
        default: () => [
          h(
            DropdownMenuTrigger,
            { asChild: true },
            {
              default: () =>
                h(
                  Button,
                  {
                    variant: "ghost",
                    size: "icon",
                    "aria-label": "Open menu",
                  },
                  { default: () => h(MoreVertical, { class: "size-4" }) },
                ),
            },
          ),
          h(DropdownMenuContent, { align: "end" }, { default: () => items }),
        ],
      });
    },
  },
];
</script>
