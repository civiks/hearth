<template>
  <DataTable
    :columns="columns"
    :data="services"
    :loading="loading"
    search-placeholder="Search services"
    :global-filter-accessor="(s) => `${s.name} ${s.category ?? ''} ${s.description ?? ''}`"
    empty-message="No services match your filters."
  >
    <template #actions>
      <Button @click="openCreate">
        <PhPlus class="size-4" weight="bold" />
        <span class="ml-1 hidden sm:inline">Add service</span>
      </Button>
    </template>
  </DataTable>

  <ResponsiveSheet
    v-if="modalOpen"
    :open="true"
    :title="editingId === null ? 'New service' : 'Edit service'"
    :description="editingId === null ? 'Add a new service to the catalog.' : `Update this service's details.`"
    body-class="space-y-5"
    @close="closeModal"
  >
    <div class="space-y-2">
      <Label for="svc_name">Service name</Label>
      <Input id="svc_name" v-model="form.name" placeholder="e.g. Kitchen Sink Repair" required />
    </div>

    <div class="space-y-2">
      <Label for="svc_category">Category</Label>
      <Select v-model="form.category">
        <SelectTrigger id="svc_category">
          <SelectValue placeholder="Select a category" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem v-for="cat in CATEGORIES" :key="cat" :value="cat">{{ cat }}</SelectItem>
        </SelectContent>
      </Select>
    </div>

    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <Label for="svc_desc">
          Description
          <span class="font-normal text-muted-foreground">(optional)</span>
        </Label>
        <div class="flex items-center gap-3">
          <button
            v-if="aiDescription"
            type="button"
            class="text-xs text-muted-foreground hover:text-foreground transition"
            @click="aiDescription = false"
          >
            Edit
          </button>
          <button
            type="button"
            class="flex items-center gap-1.5 text-xs text-primary hover:text-primary/80 transition disabled:opacity-40"
            :disabled="!form.name || generating"
            @click="onGenerate"
          >
            <AiMark class="size-3.5" />
            {{ generating ? "Generating…" : "Generate" }}
          </button>
        </div>
      </div>
      <AiSurface v-if="aiDescription" class="px-3 py-2.5 text-sm leading-relaxed">
        <span v-html="descriptionStr" />
        <span
          v-if="generating"
          class="inline-block size-2 bg-muted-foreground/60 align-middle ml-1 animate-pulse"
          aria-hidden="true"
        />
      </AiSurface>
      <Textarea
        v-else
        id="svc_desc"
        v-model="descriptionStr"
        rows="3"
        placeholder="Brief description of what's included…"
      />
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div class="space-y-2">
        <Label for="svc_price">Base price (₹)</Label>
        <Input id="svc_price" v-model.number="form.base_price" type="number" min="1" required />
      </div>
      <div class="space-y-2">
        <Label for="svc_time">Duration (min)</Label>
        <Input id="svc_time" v-model.number="form.time_required" type="number" min="1" required />
      </div>
    </div>

    <div v-if="editingId !== null" class="flex items-center justify-between gap-6 border-t pt-4">
      <div class="min-w-0">
        <Label>Active</Label>
        <p class="text-xs text-muted-foreground mt-0.5">Visible to customers and available for booking.</p>
      </div>
      <Switch v-model="form.is_active" />
    </div>

    <Alert v-if="errorMessage" variant="destructive">
      <PhWarningCircle class="size-4" weight="bold" />
      <AlertDescription>{{ errorMessage }}</AlertDescription>
    </Alert>

    <template #footer>
      <Button type="button" variant="secondary" @click="closeModal">Cancel</Button>
      <Button type="button" class="flex-1" :disabled="submitting" @click="submitService">
        {{ submitting ? "Saving…" : editingId === null ? "Create service" : "Save changes" }}
      </Button>
    </template>
  </ResponsiveSheet>
</template>

<script lang="ts" setup>
import {
  PhWarningCircle,
  PhPencilSimple,
  PhPlus,
  PhTrash,
} from '@phosphor-icons/vue';
import { computed, h, reactive, ref } from "vue";
import type { ColumnDef } from "@tanstack/vue-table";

import AiMark from "@/components/AiMark.vue";
import AiSurface from "@/components/AiSurface.vue";
import RowActions from "@/components/RowActions.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ResponsiveSheet from "@/components/ui/ResponsiveSheet.vue";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, api } from "@/lib/api";
import { CATEGORY_NAMES as CATEGORIES } from "@/lib/categories";
import { generateServiceDescription, type AgentEvent } from "@/lib/genai";

export interface AdminService {
  id: number;
  name: string;
  description: string | null;
  category: string | null;
  base_price: number;
  time_required: number;
  is_active: boolean;
}

const props = defineProps<{ services: AdminService[]; loading?: boolean }>();
const emit = defineEmits<{ delete: [id: number]; changed: [] }>();
void props;

const modalOpen = ref(false);
const editingId = ref<number | null>(null);
const submitting = ref(false);
const generating = ref(false);
const aiDescription = ref(false);
const errorMessage = ref("");

const form = reactive({
  name: "",
  description: "" as string | null,
  category: "" as string,
  base_price: 0,
  time_required: 0,
  is_active: true,
});

const descriptionStr = computed<string>({
  get: () => form.description ?? "",
  set: (v: string) => { form.description = v; },
});

const columns: ColumnDef<AdminService>[] = [
  {
    accessorKey: "name",
    header: "Service",
    enableSorting: true,
    meta: { label: "Service" },
    cell: ({ row }) => {
      const s = row.original;
      return h("div", { class: "space-y-0.5" }, [
        h("div", { class: "font-medium" }, s.name),
        s.category ? h("div", { class: "text-xs text-muted-foreground" }, s.category) : null,
      ]);
    },
  },
  {
    accessorKey: "base_price",
    header: "Price",
    enableSorting: true,
    meta: { label: "Price", nowrap: true, align: "right", mono: true },
    cell: ({ row }) => `₹${row.original.base_price}`,
  },
  {
    accessorKey: "time_required",
    header: "Duration",
    enableSorting: true,
    meta: { label: "Duration", nowrap: true, align: "right", mono: true },
    cell: ({ row }) => `${row.original.time_required} min`,
  },
  {
    accessorKey: "is_active",
    header: "Status",
    enableSorting: true,
    meta: { label: "Status", nowrap: true },
    cell: ({ row }) => h(StatusBadge, { status: row.original.is_active ? "active" : "inactive" }),
  },
  {
    id: "actions",
    header: "",
    enableSorting: false,
    enableHiding: false,
    meta: { align: "right" },
    cell: ({ row }) => {
      const s = row.original;
      return h(RowActions, {
        actions: [
          { label: "Edit", icon: PhPencilSimple, onClick: () => openEdit(s) },
          { label: "Delete", icon: PhTrash, variant: "destructive", onClick: () => emit("delete", s.id) },
        ],
      });
    },
  },
];

function openCreate() {
  editingId.value = null;
  Object.assign(form, { name: "", description: "", category: "", base_price: 0, time_required: 0, is_active: true });
  aiDescription.value = false;
  errorMessage.value = "";
  modalOpen.value = true;
}

function openEdit(service: AdminService) {
  editingId.value = service.id;
  Object.assign(form, {
    name: service.name,
    description: service.description ?? "",
    category: service.category ?? "",
    base_price: service.base_price,
    time_required: service.time_required,
    is_active: service.is_active,
  });
  aiDescription.value = false;
  errorMessage.value = "";
  modalOpen.value = true;
}

function closeModal() {
  modalOpen.value = false;
}

async function onGenerate() {
  if (!form.name || generating.value) return;
  generating.value = true;
  aiDescription.value = true;
  form.description = "";
  const stream = generateServiceDescription(form.name, form.category || "General");
  const reader = stream.getReader();
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      if ((value as AgentEvent).type === "text") form.description = (form.description ?? "") + (value as { type: "text"; delta: string }).delta;
    }
  } finally {
    generating.value = false;
  }
}

async function submitService() {
  if (submitting.value) return;
  if (form.base_price <= 0 || form.time_required <= 0) {
    errorMessage.value = "Price and duration must be greater than 0.";
    return;
  }
  submitting.value = true;
  errorMessage.value = "";
  try {
    const payload = {
      name: form.name,
      description: form.description || null,
      category: form.category || null,
      base_price: form.base_price,
      time_required: form.time_required,
      ...(editingId.value !== null && { is_active: form.is_active }),
    };
    if (editingId.value === null) {
      await api.post("/api/services", payload);
    } else {
      await api.put(`/api/services/${editingId.value}`, payload);
    }
    emit("changed");
    closeModal();
  } catch (err) {
    errorMessage.value = err instanceof ApiError ? err.detail : "Failed to save service.";
  } finally {
    submitting.value = false;
  }
}
</script>
