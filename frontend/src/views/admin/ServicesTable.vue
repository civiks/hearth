<template>
  <section class="flex flex-col gap-4 min-h-[640px] min-w-0">
    <header
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <div>
        <h2 class="text-base font-medium">Services</h2>
        <p class="text-xs text-muted-foreground">
          Catalog of services available to customers.
        </p>
      </div>
      <div class="flex flex-col sm:flex-row gap-2">
        <div class="relative w-full sm:w-64">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            v-model="search"
            placeholder="Search services"
            aria-label="Search services"
            class="pl-9"
          />
        </div>
        <Button @click="openCreate">
          <Plus class="mr-2 size-4" />
          Add service
        </Button>
      </div>
    </header>

    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Description</TableHead>
          <TableHead>Base price</TableHead>
          <TableHead>Time required</TableHead>
          <TableHead class="w-12"></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="service in pageItems" :key="service.id">
          <TableCell class="font-medium">{{ service.name }}</TableCell>
          <TableCell class="text-muted-foreground max-w-md">
            {{ service.description }}
          </TableCell>
          <TableCell>₹{{ service.base_price }}</TableCell>
          <TableCell>{{ service.time_required }} min</TableCell>
          <TableCell>
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button variant="ghost" size="icon" aria-label="Open menu">
                  <MoreVertical class="size-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem @click="openEdit(service)">
                  <Edit2 class="mr-2 size-4" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem
                  class="text-destructive focus:text-destructive"
                  @click="$emit('delete', service.id)"
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
            <Button type="button" variant="secondary" @click="closeModal">Cancel</Button>
            <Button type="submit" :disabled="submitting">
              {{ editingId === null ? "Create service" : "Update service" }}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  </section>
</template>

<script lang="ts" setup>
import { AlertCircle, Edit2, MoreVertical, Plus, Search, Trash2 } from "lucide-vue-next";
import { computed, reactive, ref, watch } from "vue";

import Pagination from "@/components/Pagination.vue";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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

const search = ref("");
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

const filtered = computed(() => {
  if (!search.value) return props.services;
  const q = search.value.toLowerCase().trim();
  return props.services.filter((s) => s.name.toLowerCase().includes(q));
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

function openCreate() {
  editingId.value = null;
  Object.assign(form, { name: "", description: "", base_price: 0, time_required: 0 });
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

// emit is used inside submitService; void it here to suppress unused warnings when narrowing types
void emit;
</script>
