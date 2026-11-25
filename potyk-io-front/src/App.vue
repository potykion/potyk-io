<script setup lang="ts">
import ConfirmDialog from "primevue/confirmdialog";
import Toast from "primevue/toast";
import { RouterView } from "vue-router";
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <a class="brand" href="/money/">potyk-money</a>
      <a class="legacy" href="/fin/">← старый учёт</a>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
  <Toast position="top-right" />
  <ConfirmDialog />
</template>

<style scoped>
.app-shell {
  max-width: 56rem;
  margin: 0 auto;
  padding: 1.25rem 1rem 3rem;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.brand {
  font-size: 1.25rem;
  font-weight: 700;
  text-decoration: none;
  letter-spacing: -0.02em;
}

.legacy {
  color: #64748b;
  text-decoration: none;
  font-size: 0.9rem;
}

.app-main {
  min-height: 50vh;
}
</style>
