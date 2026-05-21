<template>
  <section class="flex flex-col gap-4 min-h-[640px] min-w-0">
    <header
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <div>
        <h2 class="text-base font-medium">Users</h2>
        <p class="text-xs text-muted-foreground">Registered customers on the platform.</p>
      </div>
      <div class="relative w-full sm:w-64">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
        <Input
          v-model="search"
          placeholder="Search users"
          aria-label="Search users"
          class="pl-9"
        />
      </div>
    </header>

    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Pincode</TableHead>
          <TableHead>Status</TableHead>
          <TableHead class="w-12"></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="u in pageItems" :key="u.id">
          <TableCell>
            <div class="flex items-center gap-3">
              <UserAvatar :name="u.full_name" :variant="u.is_blocked ? 'danger' : 'primary'" />
              <div class="leading-tight">
                <RouterLink
                  :to="`/users/${u.id}`"
                  class="text-sm font-medium hover:text-primary"
                >
                  {{ u.full_name }}
                </RouterLink>
                <div class="text-xs text-muted-foreground">{{ u.email }}</div>
              </div>
            </div>
          </TableCell>
          <TableCell>{{ u.pincode }}</TableCell>
          <TableCell><StatusBadge :status="u.is_blocked ? 'blocked' : 'active'" /></TableCell>
          <TableCell>
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button variant="ghost" size="icon" aria-label="Open menu">
                  <MoreVertical class="size-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem @click="$emit('toggleBlock', u)">
                  <component :is="u.is_blocked ? Unlock : Lock" class="mr-2 size-4" />
                  {{ u.is_blocked ? "Unblock" : "Block" }}
                </DropdownMenuItem>
                <DropdownMenuItem
                  class="text-destructive focus:text-destructive"
                  @click="$emit('delete', u.id)"
                >
                  <Trash2 class="mr-2 size-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <Pagination
      class="mt-auto"
      :page="page"
      :page-size="PAGE_SIZE"
      :total="filtered.length"
      @update:page="page = $event"
    />
  </section>
</template>

<script lang="ts" setup>
import { Lock, MoreVertical, Search, Trash2, Unlock } from "lucide-vue-next";
import { computed, ref, watch } from "vue";
import { RouterLink } from "vue-router";

import UserAvatar from "@/components/Avatar.vue";
import Pagination from "@/components/Pagination.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { AdminUser } from "./ProfessionalsTable.vue";

const props = defineProps<{ users: AdminUser[] }>();
defineEmits<{
  toggleBlock: [user: AdminUser];
  delete: [id: number];
}>();

const search = ref("");

const filtered = computed(() => {
  if (!search.value) return props.users;
  const q = search.value.toLowerCase().trim();
  return props.users.filter(
    (u) =>
      u.full_name.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q) ||
      (u.pincode ?? "").includes(q),
  );
});

const PAGE_SIZE = 10;
const page = ref(1);
const pageItems = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return filtered.value.slice(start, start + PAGE_SIZE);
});
watch(search, () => {
  page.value = 1;
});
</script>
