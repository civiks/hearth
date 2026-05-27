<template>
  <DataTable
    :columns="columns"
    :data="professionals"
    :loading="loading"
    search-placeholder="Search professionals"
    :global-filter-accessor="
      (p) => `${p.full_name} ${p.email} ${p.pincode ?? ''}`
    "
    empty-message="No professionals match your filters."
  />
</template>

<script lang="ts" setup>
import { CheckCircle, Trash2, XCircle } from "lucide-vue-next";
import { h } from "vue";
import { RouterLink } from "vue-router";
import type { ColumnDef } from "@tanstack/vue-table";

import RowActions from "@/components/RowActions.vue";
import UserAvatar, { type AvatarVariant } from "@/components/Avatar.vue";
import ApprovalSummaryChip from "@/components/genai/ApprovalSummaryChip.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { DataTable } from "@/components/ui/data-table";

export interface AdminUser {
  id: number;
  email: string;
  full_name: string;
  role: string | null;
  pincode: string | null;
  experience?: number | null;
  approval_status?: string | null;
  is_blocked: boolean;
  description?: string | null;
  service_name?: string | null;
}

const props = defineProps<{ professionals: AdminUser[]; loading?: boolean }>();
const emit = defineEmits<{
  approve: [id: number];
  reject: [id: number];
  delete: [id: number];
}>();

function avatarVariant(u: AdminUser): AvatarVariant {
  if (u.is_blocked) return "danger";
  if (u.approval_status === "pending") return "warning";
  if (u.approval_status === "rejected") return "danger";
  if (u.approval_status === "approved") return "success";
  return "primary";
}

const columns: ColumnDef<AdminUser>[] = [
  {
    accessorKey: "full_name",
    header: "Name",
    enableSorting: true,
    meta: { label: "Name" },
    cell: ({ row }) => {
      const u = row.original;
      return h(
        "div",
        { class: "flex items-center gap-3 min-w-0" },
        [
          h(UserAvatar, {
            name: u.full_name,
            variant: avatarVariant(u),
          }),
          h(
            "div",
            { class: "leading-tight min-w-0" },
            [
              h(
                RouterLink,
                {
                  to: `/users/${u.id}`,
                  class: "text-sm font-medium hover:text-primary truncate block",
                },
                () => u.full_name,
              ),
              h(
                "div",
                { class: "text-xs text-muted-foreground truncate" },
                u.email,
              ),
            ],
          ),
        ],
      );
    },
  },
  {
    accessorKey: "experience",
    header: "Experience",
    enableSorting: true,
    meta: { label: "Experience", nowrap: true, align: "right" },
    cell: ({ row }) => `${row.original.experience ?? 0} yrs`,
  },
  {
    accessorKey: "pincode",
    header: "Pincode",
    enableSorting: true,
    meta: { label: "Pincode", nowrap: true },
    cell: ({ row }) => row.original.pincode ?? "—",
  },
  {
    id: "approval_status",
    accessorFn: (u) => u.approval_status ?? "pending",
    header: "Status",
    enableSorting: true,
    filterFn: (row, _id, value: string[]) =>
      value.includes(row.original.approval_status ?? "pending"),
    meta: {
      label: "Status",
      filterOptions: [
        { label: "Approved", value: "approved" },
        { label: "Pending", value: "pending" },
        { label: "Rejected", value: "rejected" },
      ],
    },
    cell: ({ row }) => {
      const u = row.original;
      const isPending = (u.approval_status ?? "pending") === "pending";
      return h(
        "div",
        { class: "flex flex-col items-start gap-1.5" },
        [
          h(StatusBadge, { status: u.approval_status ?? "pending" }),
          isPending
            ? h(ApprovalSummaryChip, {
                professional: u,
                cohort: props.professionals,
              })
            : null,
        ],
      );
    },
  },
  {
    id: "actions",
    header: "",
    enableSorting: false,
    enableHiding: false,
    meta: { align: "right" },
    cell: ({ row }) => {
      const u = row.original;
      const actions = [];
      if (u.approval_status === "pending") {
        actions.push({ label: "Approve", icon: CheckCircle, onClick: () => emit("approve", u.id) });
        actions.push({ label: "Reject", icon: XCircle, onClick: () => emit("reject", u.id) });
      }
      actions.push({ label: "Delete", icon: Trash2, variant: "destructive" as const, onClick: () => emit("delete", u.id) });
      return h(RowActions, { actions });
    },
  },
];

</script>
