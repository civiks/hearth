<template>
  <DataTable
    :columns="columns"
    :data="users"
    :loading="loading"
    search-placeholder="Search users"
    :global-filter-accessor="
      (u) => `${u.full_name} ${u.email} ${u.pincode ?? ''}`
    "
    empty-message="No users match your filters."
  />
</template>

<script lang="ts" setup>
import {
  PhLock,
  PhTrash,
  PhLockOpen,
} from '@phosphor-icons/vue';
import { h } from "vue";
import { RouterLink } from "vue-router";
import type { ColumnDef } from "@tanstack/vue-table";

import RowActions from "@/components/RowActions.vue";
import UserAvatar from "@/components/Avatar.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { DataTable } from "@/components/ui/data-table";
import type { AdminUser } from "./ProfessionalsTable.vue";

const props = defineProps<{ users: AdminUser[]; loading?: boolean }>();
const emit = defineEmits<{
  toggleBlock: [user: AdminUser];
  delete: [id: number];
}>();
void props;

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
            variant: u.is_blocked ? "danger" : "primary",
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
    accessorKey: "pincode",
    header: "Pincode",
    enableSorting: true,
    meta: { label: "Pincode", nowrap: true, mono: true },
    cell: ({ row }) => row.original.pincode ?? "—",
  },
  {
    id: "status",
    accessorFn: (u) => (u.is_blocked ? "blocked" : "active"),
    header: "Status",
    enableSorting: true,
    filterFn: (row, _id, value: string[]) =>
      value.includes(row.original.is_blocked ? "blocked" : "active"),
    meta: {
      label: "Status",
      filterOptions: [
        { label: "Active", value: "active" },
        { label: "Blocked", value: "blocked" },
      ],
    },
    cell: ({ row }) =>
      h(StatusBadge, {
        status: row.original.is_blocked ? "blocked" : "active",
      }),
  },
  {
    id: "actions",
    header: "",
    enableSorting: false,
    enableHiding: false,
    meta: { align: "right" },
    cell: ({ row }) => {
      const u = row.original;
      return h(RowActions, {
        actions: [
          {
            label: u.is_blocked ? "Unblock" : "Block",
            icon: u.is_blocked ? PhLockOpen : PhLock,
            onClick: () => emit("toggleBlock", u),
          },
          { label: "Delete", icon: PhTrash, variant: "destructive" as const, onClick: () => emit("delete", u.id) },
        ],
      });
    },
  },
];
</script>
