<template>
  <div class="px-6 py-8 flex flex-col gap-4 min-h-[700px] min-w-0">
    <header>
      <h1 class="text-2xl font-light tracking-tight">All service requests</h1>
      <p class="text-sm text-muted-foreground">
        Read-only view of every request on the platform.
      </p>
    </header>

    <div
      v-if="!requests.length"
      class="border bg-card p-12 text-center text-sm text-muted-foreground"
    >
      No service requests yet
    </div>

    <template v-else>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Service</TableHead>
            <TableHead>Customer</TableHead>
            <TableHead>Scheduled</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Pincode</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="r in pageItems" :key="r.id">
            <TableCell class="font-medium">{{ r.service_name }}</TableCell>
            <TableCell>{{ r.customer_name }}</TableCell>
            <TableCell>{{ formatDateTime(r.scheduled_time) }}</TableCell>
            <TableCell><StatusBadge :status="r.service_status" /></TableCell>
            <TableCell>{{ r.pincode }}</TableCell>
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
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from "vue";

import Pagination from "@/components/Pagination.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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

const PAGE_SIZE = 10;
const page = ref(1);
const pageItems = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return requests.value.slice(start, start + PAGE_SIZE);
});

onMounted(async () => {
  try {
    requests.value = await api.get<AdminRequest[]>("/api/requests");
  } catch (err) {
    console.error("requests fetch failed", err);
  }
});
</script>
