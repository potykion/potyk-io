<script setup lang="ts">
import Button from "primevue/button";
import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fetchMe } from "@/api/auth";
import { ApiError } from "@/api/client";
import { fetchRest, type RestRestaurant } from "@/api/rest";
import RestTierList from "@/components/rest/RestTierList.vue";

const router = useRouter();
const loading = ref(true);
const error = ref("");
const loggedIn = ref(false);
const restaurants = ref<RestRestaurant[]>([]);
const cuisines = ref<string[]>([]);
const selectedCuisine = ref<string | null>(null);

const tierItems = computed(() => {
  const cuisine = selectedCuisine.value;
  if (!cuisine) return [];
  const key = cuisine.toLowerCase();
  return restaurants.value.filter((r) => r.cuisine.toLowerCase() === key && r.tier);
});

const allList = computed(() => restaurants.value);

onMounted(async () => {
  loggedIn.value = (await fetchMe()) !== null;
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

function hrefFor(item: RestRestaurant): string {
  return item.maps_url || "#";
}
</script>

<template>
  <section class="rest-page">
    <div class="rest-header">
      <h1>Рестораны</h1>
      <Button
        v-if="loggedIn"
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
      <p v-if="!restaurants.length" class="empty">Пока пусто</p>
      <template v-else>
        <div v-if="cuisines.length" class="chips" role="group" aria-label="Кухни">
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
        <ul v-else class="rest-list">
          <li v-for="item in allList" :key="item.id" class="rest-item">
            <a
              class="rest-link"
              :href="hrefFor(item)"
              :target="item.maps_url ? '_blank' : undefined"
              :rel="item.maps_url ? 'noopener noreferrer' : undefined"
            >
              <img v-if="item.logo" class="thumb" :src="item.logo" :alt="item.name" />
              <span v-else class="thumb thumb--empty" aria-hidden="true" />
              <span class="meta">
                <strong>{{ item.name }}</strong>
                <span class="sub"
                  >{{ item.cuisine }}<template v-if="item.tier"> · {{ item.tier }}</template></span
                >
              </span>
            </a>
          </li>
        </ul>
      </template>
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

.empty {
  color: #64748b;
  margin: 0.5rem 0 0;
}

.rest-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.rest-item {
  border-bottom: 1px solid #e2e8f0;
}

.rest-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0;
  text-decoration: none;
  color: inherit;
  min-width: 0;
}

.rest-link:hover strong {
  text-decoration: underline;
}

.thumb {
  width: 44px;
  height: 44px;
  object-fit: cover;
  border-radius: 4px;
  flex: 0 0 auto;
  background: #e2e8f0;
}

.thumb--empty {
  display: block;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.meta strong {
  font-size: 1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sub {
  color: #64748b;
  font-size: 0.85rem;
}
</style>
