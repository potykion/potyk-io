<script setup lang="ts">
import Button from "primevue/button";
import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ApiError } from "@/api/client";
import { fetchRest, type RestRestaurant } from "@/api/rest";
import RestTierList from "@/components/rest/RestTierList.vue";

const router = useRouter();
const loading = ref(true);
const error = ref("");
const restaurants = ref<RestRestaurant[]>([]);
const cuisines = ref<string[]>([]);
const selectedCuisine = ref<string | null>(null);

const tierItems = computed(() => {
  const cuisine = selectedCuisine.value;
  if (!cuisine) return [];
  const key = cuisine.toLowerCase();
  return restaurants.value.filter((r) => r.cuisine.toLowerCase() === key && r.tier);
});

onMounted(async () => {
  try {
    const state = await fetchRest();
    restaurants.value = state.restaurants;
    cuisines.value = state.cuisines;
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : "Не удалось загрузить";
  } finally {
    loading.value = false;
  }
});

function selectCuisine(cuisine: string): void {
  selectedCuisine.value = selectedCuisine.value === cuisine ? null : cuisine;
}

function openAdmin(): void {
  void router.push({ name: "rest-admin" });
}
</script>

<template>
  <section class="rest-page">
    <div class="rest-header">
      <h1>Рестораны</h1>
      <Button
        type="button"
        label="Админка"
        severity="secondary"
        text
        icon="pi pi-cog"
        @click="openAdmin"
      />
    </div>

    <div v-if="loading" class="state">
      <ProgressSpinner style="width: 2.5rem; height: 2.5rem" />
    </div>
    <Message v-else-if="error" severity="error">{{ error }}</Message>
    <template v-else>
      <p v-if="!cuisines.length" class="empty">Пока пусто — добавь ресторан в админке</p>
      <div v-else class="chips" role="group" aria-label="Кухни">
        <Button
          v-for="cuisine in cuisines"
          :key="cuisine"
          type="button"
          :label="cuisine"
          severity="secondary"
          :outlined="selectedCuisine !== cuisine"
          size="small"
          @click="selectCuisine(cuisine)"
        />
      </div>

      <RestTierList
        v-if="selectedCuisine"
        :items="tierItems"
        :label="`Тирлист: ${selectedCuisine}`"
      />
      <p v-else-if="cuisines.length" class="hint">Выбери кухню — покажем тирлист</p>
    </template>
  </section>
</template>

<style scoped>
.rest-page h1 {
  margin: 0;
  font-size: 1.5rem;
  letter-spacing: -0.02em;
}

.rest-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.state {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.hint,
.empty {
  color: #64748b;
  margin: 0.5rem 0 0;
}
</style>
