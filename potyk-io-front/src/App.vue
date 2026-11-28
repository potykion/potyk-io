<script setup lang="ts">
import ConfirmDialog from "primevue/confirmdialog";
import Toast from "primevue/toast";
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";

const route = useRoute();
const isFin = computed(() => route.name === "fin");
const isRestAdmin = computed(() => route.name === "rest-admin");
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <RouterLink class="brand" :to="{ name: 'index' }">potyk-io</RouterLink>
      <a v-if="isFin" class="legacy" href="/fin/">← старый учёт</a>
      <RouterLink v-else-if="isRestAdmin" class="legacy" :to="{ name: 'rest' }"
        >← рестораны</RouterLink
      >
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
  width: 100%;
  max-width: 56rem;
  margin: 0 auto;
  padding: 1.25rem 1rem 3rem;
  box-sizing: border-box;
  overflow-x: clip;
  min-width: 0;
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
