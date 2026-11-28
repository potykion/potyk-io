<script setup lang="ts">
import AutoComplete, { type AutoCompleteCompleteEvent } from "primevue/autocomplete";
import Button from "primevue/button";
import FileUpload, { type FileUploadSelectEvent } from "primevue/fileupload";
import InputText from "primevue/inputtext";
import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";
import Select from "primevue/select";
import { useToast } from "primevue/usetoast";
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ApiError } from "@/api/client";
import { createRest, fetchRest, type RestRestaurant } from "@/api/rest";

const TIERS = ["S", "A", "B", "C", "D"];
const LOGO_ACCEPT = "image/png,image/jpeg,image/webp,image/gif";

const router = useRouter();
const toast = useToast();

const loading = ref(true);
const busy = ref(false);
const error = ref("");
const restaurants = ref<RestRestaurant[]>([]);
const cuisines = ref<string[]>([]);
const cuisineSuggestions = ref<string[]>([]);
const logoFile = ref<File | null>(null);
const logoPreviewUrl = ref("");
const fileUploadKey = ref(0);

const form = reactive({
  name: "",
  cuisine: "",
  tier: "B",
  maps_url: "",
});

const logoLabel = computed(() => logoFile.value?.name || "Файл не выбран");

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

onBeforeUnmount(() => {
  clearLogoPreview();
});

function clearLogoPreview(): void {
  if (logoPreviewUrl.value) {
    URL.revokeObjectURL(logoPreviewUrl.value);
    logoPreviewUrl.value = "";
  }
}

function clearLogo(): void {
  clearLogoPreview();
  logoFile.value = null;
  fileUploadKey.value += 1;
}

function onLogoSelect(event: FileUploadSelectEvent): void {
  const file = event.files?.[0];
  if (!file) return;
  clearLogoPreview();
  logoFile.value = file;
  logoPreviewUrl.value = URL.createObjectURL(file);
}

function searchCuisine(event: AutoCompleteCompleteEvent): void {
  const q = String(event.query || "")
    .trim()
    .toLowerCase();
  cuisineSuggestions.value = q
    ? cuisines.value.filter((c) => c.toLowerCase().includes(q))
    : [...cuisines.value];
}

async function submit(): Promise<void> {
  busy.value = true;
  error.value = "";
  try {
    const state = await createRest({
      name: form.name.trim(),
      cuisine: String(form.cuisine || "").trim(),
      tier: form.tier,
      maps_url: form.maps_url.trim(),
      logo: logoFile.value,
    });
    restaurants.value = state.restaurants;
    cuisines.value = state.cuisines;
    form.name = "";
    form.cuisine = "";
    form.maps_url = "";
    form.tier = "B";
    clearLogo();
    toast.add({ severity: "success", summary: "Ресторан добавлен", life: 2000 });
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : "Не удалось сохранить";
  } finally {
    busy.value = false;
  }
}

function openRest(): void {
  void router.push({ name: "rest" });
}
</script>

<template>
  <section class="rest-admin">
    <div class="rest-header">
      <h1>Админка ресторанов</h1>
      <Button
        type="button"
        label="К списку"
        severity="secondary"
        text
        icon="pi pi-arrow-left"
        @click="openRest"
      />
    </div>

    <div v-if="loading" class="state">
      <ProgressSpinner style="width: 2.5rem; height: 2.5rem" />
    </div>
    <template v-else>
      <Message v-if="error" severity="error" class="err">{{ error }}</Message>

      <form class="form" @submit.prevent="submit">
        <label class="field">
          <span>Название</span>
          <InputText v-model="form.name" required placeholder="Mimi" />
        </label>
        <label class="field">
          <span>Кухня</span>
          <AutoComplete
            v-model="form.cuisine"
            :suggestions="cuisineSuggestions"
            dropdown
            :force-selection="false"
            placeholder="Грузия"
            @complete="searchCuisine"
          />
        </label>
        <label class="field">
          <span>Тир</span>
          <Select v-model="form.tier" :options="TIERS" placeholder="Тир" />
        </label>
        <div class="field">
          <span>Лого</span>
          <div class="logo-row">
            <FileUpload
              :key="fileUploadKey"
              mode="basic"
              :accept="LOGO_ACCEPT"
              choose-label="Выбрать файл"
              :auto="false"
              :custom-upload="true"
              :disabled="busy"
              @select="onLogoSelect"
            />
            <Button
              v-if="logoFile"
              type="button"
              label="Сбросить"
              severity="secondary"
              text
              :disabled="busy"
              @click="clearLogo"
            />
          </div>
          <p class="logo-name">{{ logoLabel }}</p>
          <img
            v-if="logoPreviewUrl"
            class="logo-preview"
            :src="logoPreviewUrl"
            alt="Превью лого"
          />
        </div>
        <label class="field full">
          <span>Я.Карты</span>
          <InputText v-model="form.maps_url" placeholder="https://yandex.ru/maps/-/…" />
        </label>
        <div class="actions">
          <Button type="submit" label="Добавить" :loading="busy" />
        </div>
      </form>

      <h2 class="list-title">Уже в базе</h2>
      <ul v-if="restaurants.length" class="list">
        <li v-for="r in restaurants" :key="r.id" class="list-item">
          <img v-if="r.logo" class="thumb" :src="r.logo" :alt="r.name" />
          <div class="meta">
            <strong>{{ r.name }}</strong>
            <span>{{ r.cuisine }} · {{ r.tier || "—" }}</span>
          </div>
        </li>
      </ul>
      <p v-else class="empty">Пока пусто</p>
    </template>
  </section>
</template>

<style scoped>
.rest-admin h1 {
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

.err {
  margin-bottom: 1rem;
}

.form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem 1rem;
  margin-bottom: 2rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.field span {
  font-size: 0.85rem;
  color: #64748b;
}

.field.full {
  grid-column: 1 / -1;
}

.field :deep(.p-inputtext),
.field :deep(.p-autocomplete),
.field :deep(.p-select) {
  width: 100%;
}

.logo-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
}

.logo-name {
  margin: 0;
  font-size: 0.85rem;
  color: #64748b;
}

.logo-preview {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 4px;
  margin-top: 0.25rem;
}

.actions {
  grid-column: 1 / -1;
}

.list-title {
  margin: 0 0 0.75rem;
  font-size: 1.1rem;
}

.list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.thumb {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
  flex: 0 0 auto;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.meta span {
  color: #64748b;
  font-size: 0.85rem;
}

.empty {
  color: #64748b;
  margin: 0;
}

@media screen and (max-width: 600px) {
  .form {
    grid-template-columns: 1fr;
  }
}
</style>
