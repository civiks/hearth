<template>
  <DataTable
    :columns="columns"
    :data="services"
    title="Services"
    description="Catalog of services available to customers."
    search-placeholder="Search services"
    :global-filter-accessor="(s) => `${s.name} ${s.description ?? ''}`"
    empty-message="No services match your filters."
  >
    <template #actions>
      <Button @click="openCreate">
        <Plus class="size-4" />
        <span class="ml-1">Add</span>
      </Button>
    </template>
  </DataTable>

  <Dialog :open="modalOpen" @update:open="(v) => !v && closeModal()">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>
          {{ editingId === null ? "Create new service" : "Edit service" }}
        </DialogTitle>
      </DialogHeader>
      <form class="space-y-4" @submit.prevent="submitService">
        <div class="space-y-2">
          <Label for="svc_name">Service name</Label>
          <Input id="svc_name" v-model="form.name" required />
        </div>
        <div class="space-y-2">
          <Label for="svc_desc">Description</Label>
          <Textarea id="svc_desc" v-model="descriptionStr" rows="2" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-2">
            <Label for="svc_price">Base price (₹)</Label>
            <Input
              id="svc_price"
              v-model.number="form.base_price"
              type="number"
              min="0"
              required
            />
          </div>
          <div class="space-y-2">
            <Label for="svc_time">Time required (min)</Label>
            <Input
              id="svc_time"
              v-model.number="form.time_required"
              type="number"
              min="0"
              required
            />
          </div>
        </div>
        <Alert v-if="errorMessage" variant="destructive">
          <AlertCircle class="size-4" />
          <AlertDescription>{{ errorMessage }}</AlertDescription>
        </Alert>
        <DialogFooter>
          <Button type="button" variant="secondary" @click="closeModal">
            Cancel
          </Button>
          <Button type="submit" :disabled="submitting">
            {{ editingId === null ? "Create service" : "Update service" }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>

<script lang="ts" setup>
import {
  AlertCircle,
  Edit2,
  MoreVertical,
  Plus,
  Trash2,
} from "lucide-vue-next";
import { computed, h, reactive, ref } from "vue";
import type { ColumnDef } from "@tanstack/vue-table";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, api } from "@/lib/api";

export interface AdminService {
  id: number;
  name: string;
  description: string | null;
  base_price: number;
  time_required: number;
}

const props = defineProps<{ services: AdminService[] }>();
const emit = defineEmits<{ delete: [id: number]; changed: [] }>();
void props;

const modalOpen = ref(false);
const editingId = ref<number | null>(null);
const submitting = ref(false);
const errorMessage = ref("");

const form = reactive({
  name: "",
  description: "" as string | null,
  base_price: 0,
  time_required: 0,
});

const descriptionStr = computed<string>({
  get: () => form.description ?? "",
  set: (v: string) => {
    form.description = v;
  },
});

const columns: ColumnDef<AdminService>[] = [
  {
    accessorKey: "name",
    header: "Name",
    enableSorting: true,
    meta: { label: "Name", cellClass: "font-medium" },
  },
  {
    accessorKey: "description",
    header: "Description",
    enableSorting: false,
    meta: { label: "Description", cellClass: "text-muted-foreground max-w-md" },
    cell: ({ row }) => row.original.description ?? "—",
  },
  {
    accessorKey: "base_price",
    header: "Base price",
    enableSorting: true,
    meta: { label: "Base price", nowrap: true, align: "right" },
    cell: ({ row }) => `₹${row.original.base_price}`,
  },
  {
    accessorKey: "time_required",
    header: "Time required",
    enableSorting: true,
    meta: { label: "Time", nowrap: true, align: "right" },
    cell: ({ row }) => `${row.original.time_required} min`,
  },
  {
    id: "actions",
    header: "",
    enableSorting: false,
    enableHiding: false,
    meta: { align: "right" },
    cell: ({ row }) => {
      const s = row.original;
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
                { onClick: () => openEdit(s) },
                {
                  default: () => [h(Edit2, { class: "mr-2 size-4" }), "Edit"],
                },
              ),
              h(
                DropdownMenuItem,
                {
                  class: "text-destructive focus:text-destructive",
                  onClick: () => emit("delete", s.id),
                },
                {
                  default: () => [h(Trash2, { class: "mr-2 size-4" }), "Delete"],
                },
              ),
            ],
          }),
        ],
      });
    },
  },
];

function openCreate() {
  editingId.value = null;
  Object.assign(form, {
    name: "",
    description: "",
    base_price: 0,
    time_required: 0,
  });
  errorMessage.value = "";
  modalOpen.value = true;
}

function openEdit(service: AdminService) {
  editingId.value = service.id;
  Object.assign(form, {
    name: service.name,
    description: service.description ?? "",
    base_price: service.base_price,
    time_required: service.time_required,
  });
  errorMessage.value = "";
  modalOpen.value = true;
}

function closeModal() {
  modalOpen.value = false;
}

async function submitService() {
  if (submitting.value) return;
  if (form.base_price <= 0 || form.time_required <= 0) {
    errorMessage.value = "Base price and time required must be greater than 0.";
    return;
  }
  submitting.value = true;
  errorMessage.value = "";
  try {
    if (editingId.value === null) {
      await api.post("/api/services", form);
    } else {
      await api.put(`/api/services/${editingId.value}`, form);
    }
    emit("changed");
    closeModal();
  } catch (err) {
    errorMessage.value =
      err instanceof ApiError ? err.detail : "Failed to submit service.";
  } finally {
    submitting.value = false;
  }
}
</script>
