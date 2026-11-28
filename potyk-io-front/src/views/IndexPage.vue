<script setup lang="ts">
import Card from "primevue/card";
import { useRouter } from "vue-router";

const router = useRouter();

type Section = {
  name: string;
  title: string;
  subtitle: string;
  path: string;
  lock: boolean;
};

const sections: Section[] = [
  {
    name: "fin",
    title: "Учёт",
    subtitle: "Расходы, накопления, бюджет",
    path: "/v2/fin",
    lock: true,
  },
  {
    name: "rest",
    title: "Рестораны",
    subtitle: "Кухни и тирлист",
    path: "/v2/rest",
    lock: true,
  },
  {
    name: "rest-admin",
    title: "Админка рестов",
    subtitle: "Добавить ресторан",
    path: "/v2/admin/rest",
    lock: true,
  },
];

function open(name: string): void {
  void router.push({ name });
}

function onCardKeydown(event: KeyboardEvent, name: string): void {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    open(name);
  }
}
</script>

<template>
  <section class="index-page">
    <h1>Разделы</h1>
    <div class="index-grid">
      <Card
        v-for="section in sections"
        :key="section.name"
        class="nav-card"
        role="link"
        tabindex="0"
        :aria-label="
          section.lock
            ? `${section.title} — нужен логин, открыть ${section.path}`
            : `${section.title} — открыть ${section.path}`
        "
        @click="open(section.name)"
        @keydown="onCardKeydown($event, section.name)"
      >
        <template #title>
          <span class="nav-card__title">
            <span>{{ section.title }}</span>
            <span
              v-if="section.lock"
              class="nav-card__lock"
              title="нужен логин"
              aria-label="нужен логин"
            >🔒</span>
          </span>
        </template>
        <template #subtitle>{{ section.subtitle }}</template>
        <template #content>
          <p class="nav-card__hint">
            Открыть <span class="nav-card__path">{{ section.path }}</span>
            <i class="pi pi-arrow-right" aria-hidden="true" />
          </p>
        </template>
      </Card>
    </div>
  </section>
</template>

<style scoped>
.index-page h1 {
  margin: 0 0 1rem;
  font-size: 1.5rem;
  letter-spacing: -0.02em;
}

.index-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
  gap: 1rem;
}

.nav-card {
  cursor: pointer;
  transition:
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

.nav-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgb(15 23 42 / 10%);
}

.nav-card:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.nav-card__title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.nav-card__lock {
  flex-shrink: 0;
  font-size: 0.95rem;
  line-height: 1;
}

.nav-card__hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

.nav-card__path {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.85em;
}
</style>
