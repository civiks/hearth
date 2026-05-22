<template>
  <div class="px-6 py-8 max-w-3xl mx-auto space-y-6">
    <header>
      <h1 class="text-2xl font-light tracking-tight">Admin tools</h1>
      <p class="text-sm text-muted-foreground mt-1">
        CSV exports and Celery job triggers for testing the backend pipelines.
      </p>
    </header>

    <ExportSection />
    <BackendJobsSection />
  </div>
</template>

<script lang="ts" setup>
import BackendJobsSection from "@/views/admin/BackendJobsSection.vue";
import ExportSection from "@/views/admin/ExportSection.vue";
</script>
