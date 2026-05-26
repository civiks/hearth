<template>
  <div class="mx-auto w-full max-w-[1440px] px-6 py-8 space-y-6">
    <p class="text-xs text-muted-foreground">
      {{ history.length }} {{ history.length === 1 ? "request" : "requests" }} on your account
    </p>

    <div
      v-if="!history.length"
      class="rounded-lg bg-card soft-card p-12 text-center text-sm text-muted-foreground space-y-3"
    >
      <p>No service history yet.</p>
      <RouterLink to="/home/browse">
        <Button variant="outline" size="sm">Browse services</Button>
      </RouterLink>
    </div>

    <div v-else class="space-y-4">
      <RequestCard
        v-for="row in history"
        :key="row.id"
        :request="row"
        :service="servicesById.get(row.service_id) ?? null"
        :professional="
          row.professional_id != null
            ? (professionalsById.get(row.professional_id) ?? null)
            : null
        "
        @edit="openEdit(row)"
        @cancel="cancelRequest(row.id)"
      />
    </div>

    <EditRequestModal
      v-if="editingRequest"
      :request="editingRequest"
      @close="editingRequest = null"
      @updated="onEdited"
    />
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { Button } from "@/components/ui/button";
import { ApiError, api } from "@/lib/api";
import { useNotificationsStore } from "@/stores/notifications";
import EditRequestModal from "@/views/customer/EditRequestModal.vue";
import RequestCard, {
  type CustomerRequest,
  type RelatedProfessional,
  type RelatedService,
} from "@/views/customer/RequestCard.vue";

const toasts = useNotificationsStore();

const history = ref<CustomerRequest[]>([]);
const services = ref<RelatedService[]>([]);
const professionals = ref<RelatedProfessional[]>([]);
const editingRequest = ref<CustomerRequest | null>(null);

const servicesById = computed(() => new Map(services.value.map((s) => [s.id, s])));
const professionalsById = computed(
  () => new Map(professionals.value.map((p) => [p.id, p])),
);

onMounted(async () => {
  await Promise.all([fetchHistory(), fetchServices(), fetchProfessionals()]);
});

async function fetchHistory() {
  try {
    history.value = await api.get<CustomerRequest[]>("/api/requests");
  } catch (err) {
    console.error("history fetch failed", err);
  }
}

async function fetchServices() {
  try {
    services.value = await api.get<RelatedService[]>("/api/services");
  } catch (err) {
    console.error("services fetch failed", err);
  }
}

async function fetchProfessionals() {
  try {
    professionals.value = await api.get<RelatedProfessional[]>(
      "/api/users?role=professional",
    );
  } catch {
    professionals.value = [];
  }
}

function openEdit(request: CustomerRequest) {
  editingRequest.value = request;
}

function onEdited() {
  editingRequest.value = null;
  toasts.success("Request updated");
  fetchHistory();
}

async function cancelRequest(id: number) {
  if (!confirm("Cancel this service request?")) return;
  try {
    await api.put(`/api/requests/${id}`, { service_status: "cancelled" });
    toasts.success("Request cancelled");
    fetchHistory();
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to cancel");
  }
}
</script>
