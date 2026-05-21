<template>
  <section class="flex flex-col gap-4 min-h-[640px] min-w-0">
    <h2 class="text-base font-medium">Service requests</h2>

    <div
      v-if="!requests.length"
      class="border bg-card p-12 text-center text-sm text-muted-foreground"
    >
      No requests yet
    </div>

    <template v-else>
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Customer</TableHead>
          <TableHead>Remarks</TableHead>
          <TableHead>Schedule</TableHead>
          <TableHead>Status</TableHead>
          <TableHead class="w-12"></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="r in pageItems" :key="r.id">
          <TableCell>
            <div class="flex items-center gap-3">
              <UserAvatar :name="r.customer_name ?? ''" :variant="avatarVariant(r)" />
              <div class="leading-tight">
                <div class="text-sm font-medium">{{ r.customer_name }}</div>
                <div class="text-xs text-muted-foreground">{{ r.address }}</div>
                <div class="text-xs text-muted-foreground">{{ r.pincode }}</div>
              </div>
            </div>
          </TableCell>
          <TableCell class="text-muted-foreground max-w-xs">
            {{ r.remarks || "No remarks" }}
          </TableCell>
          <TableCell class="whitespace-nowrap">
            {{ formatDateTime(r.scheduled_time) }}
          </TableCell>
          <TableCell><StatusBadge :status="r.service_status" /></TableCell>
          <TableCell>
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button
                  variant="ghost"
                  size="icon"
                  :disabled="!hasActions(r.service_status)"
                  aria-label="Open menu"
                >
                  <MoreVertical class="size-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  v-if="r.service_status === 'requested'"
                  @click="$emit('updateStatus', r.id, 'accepted')"
                >
                  <CheckCircle class="mr-2 size-4" />
                  Accept request
                </DropdownMenuItem>
                <DropdownMenuItem
                  v-if="r.service_status === 'accepted'"
                  @click="$emit('updateStatus', r.id, 'in_progress')"
                >
                  <PlayCircle class="mr-2 size-4" />
                  Start work
                </DropdownMenuItem>
                <DropdownMenuItem
                  v-if="r.service_status === 'in_progress'"
                  @click="$emit('updateStatus', r.id, 'completed')"
                >
                  <CheckCircle class="mr-2 size-4" />
                  Mark as complete
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
      :total="requests.length"
      @update:page="page = $event"
    />
    </template>
  </section>
</template>

<script lang="ts" setup>
import { CheckCircle, MoreVertical, PlayCircle } from "lucide-vue-next";
import { computed, ref } from "vue";

import UserAvatar, { type AvatarVariant } from "@/components/Avatar.vue";
import Pagination from "@/components/Pagination.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
defineEmits<{ updateStatus: [id: number, status: string] }>();

const PAGE_SIZE = 10;
const page = ref(1);
const pageItems = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return props.requests.slice(start, start + PAGE_SIZE);
});

function hasActions(status: string): boolean {
  return ["requested", "accepted", "in_progress"].includes(status);
}

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
</script>
