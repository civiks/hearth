<template>
  <section class="flex flex-col gap-4 min-h-[640px] min-w-0">
    <h2 class="text-base font-medium">Service history</h2>

    <div v-if="!history.length" class="border bg-card p-12 text-center text-sm text-muted-foreground">
      No service history yet
    </div>

    <template v-else>
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Service</TableHead>
          <TableHead>Scheduled time</TableHead>
          <TableHead>Address</TableHead>
          <TableHead>Status</TableHead>
          <TableHead class="w-12"></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="row in pageItems" :key="row.id">
          <TableCell class="font-medium">{{ row.service_name }}</TableCell>
          <TableCell>{{ formatDateTime(row.scheduled_time) }}</TableCell>
          <TableCell class="text-muted-foreground">{{ row.address }}</TableCell>
          <TableCell>
            <StatusBadge :status="row.service_status" />
          </TableCell>
          <TableCell>
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button
                  variant="ghost"
                  size="icon"
                  :disabled="!isActionable(row.service_status)"
                  aria-label="Open menu"
                >
                  <MoreVertical class="size-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  v-if="row.service_status === 'requested'"
                  @click="$emit('edit', row)"
                >
                  <Edit2 class="mr-2 size-4" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem
                  v-if="['requested', 'accepted'].includes(row.service_status)"
                  class="text-destructive focus:text-destructive"
                  @click="$emit('cancel', row.id)"
                >
                  <XCircle class="mr-2 size-4" />
                  Cancel
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
      :total="history.length"
      @update:page="page = $event"
    />
    </template>
  </section>
</template>

<script lang="ts" setup>
import { Edit2, MoreVertical, XCircle } from "lucide-vue-next";
import { computed, ref } from "vue";

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

export interface CustomerRequest {
  id: number;
  service_id: number;
  service_name: string | null;
  scheduled_time: string | null;
  address: string;
  pincode: string;
  service_status: string;
  remarks: string | null;
}

const props = defineProps<{ history: CustomerRequest[] }>();
defineEmits<{
  edit: [request: CustomerRequest];
  cancel: [id: number];
}>();

const PAGE_SIZE = 10;
const page = ref(1);
const pageItems = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return props.history.slice(start, start + PAGE_SIZE);
});

function isActionable(status: string): boolean {
  return ["requested", "accepted"].includes(status);
}
</script>
