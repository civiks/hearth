<template>
  <DataTable
    :columns="columns"
    :data="users"
    title="Users"
    description="Registered customers on the platform."
    search-placeholder="Search users"
    :global-filter-accessor="
      (u) => `${u.full_name} ${u.email} ${u.pincode ?? ''}`
    "
    empty-message="No users match your filters."
  />
</template>

<script lang="ts" setup>
import { Lock, MoreVertical, Trash2, Unlock } from "lucide-vue-next";
import { h } from "vue";
import { RouterLink } from "vue-router";
import type { ColumnDef } from "@tanstack/vue-table";

import UserAvatar from "@/components/Avatar.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { AdminUser } from "./ProfessionalsTable.vue";

const props = defineProps<{ users: AdminUser[] }>();
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
    meta: { label: "Pincode", nowrap: true },
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
          h(DropdownMenuContent, { align: "end" }, {
            default: () => [
              h(
                DropdownMenuItem,
                { onClick: () => emit("toggleBlock", u) },
                {
                  default: () => [
                    h(u.is_blocked ? Unlock : Lock, {
                      class: "mr-2 size-4",
                    }),
                    u.is_blocked ? "Unblock" : "Block",
                  ],
                },
              ),
              h(
                DropdownMenuItem,
                {
                  class: "text-destructive focus:text-destructive",
                  onClick: () => emit("delete", u.id),
                },
                {
                  default: () => [
                    h(Trash2, { class: "mr-2 size-4" }),
                    "Delete",
                  ],
                },
              ),
            ],
          }),
        ],
      });
    },
  },
];
</script>
