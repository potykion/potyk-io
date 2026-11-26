<script setup lang="ts">
import Button from "primevue/button";
import { computed, ref, watch } from "vue";
import type { FinDay } from "@/api/fin";
import { formatRub } from "@/utils/money";

const PAGE = 5;

const props = defineProps<{
  days: FinDay[];
}>();

type RecentOp =
  | {
      key: string;
      kind: "expense";
      id: number;
      date: string;
      amount: number;
      category: string;
      description: string;
    }
  | {
      key: string;
      kind: "saving";
      id: number;
      date: string;
      amount: number;
    };

const visibleCount = ref(PAGE);

const operations = computed<RecentOp[]>(() => {
  const ops: RecentOp[] = [];
  for (const day of props.days) {
    for (const e of day.expenses) {
      ops.push({
        key: `e-${e.id}`,
        kind: "expense",
        id: e.id,
        date: e.date,
        amount: e.amount,
        category: e.category,
        description: e.description,
      });
    }
    for (const s of day.savings) {
      ops.push({
        key: `s-${s.id}`,
        kind: "saving",
        id: s.id,
        date: s.date,
        amount: s.amount,
      });
    }
  }
  ops.sort((a, b) => {
    if (a.date !== b.date) return a.date < b.date ? 1 : -1;
    return b.id - a.id;
  });
  return ops;
});

watch(
  () => operations.value.length,
  () => {
    if (visibleCount.value < PAGE) visibleCount.value = PAGE;
  },
);

const visible = computed(() => operations.value.slice(0, visibleCount.value));
const hasMore = computed(() => visibleCount.value < operations.value.length);

function loadMore(): void {
  visibleCount.value += PAGE;
}
</script>

<template>
  <section class="ops-card">
    <h2>Последние операции</h2>

    <p v-if="!operations.length" class="empty">Пока нет операций.</p>

    <ul v-else class="list">
      <li v-for="op in visible" :key="op.key" class="row" :class="op.kind">
        <template v-if="op.kind === 'expense'">
          <span class="amount">{{ formatRub(op.amount) }}</span>
          <span class="category">{{ op.category }}</span>
          <span class="date">{{ op.date }}</span>
          <span v-if="op.description" class="desc">{{ op.description }}</span>
        </template>
        <template v-else>
          <span class="amount saving">{{ formatRub(op.amount) }}</span>
          <span class="kind-label">Сейф</span>
          <span class="date">{{ op.date }}</span>
        </template>
      </li>
    </ul>

    <Button
      v-if="hasMore"
      type="button"
      label="Ещё"
      severity="secondary"
      outlined
      size="small"
      class="more"
      @click="loadMore"
    />
  </section>
</template>

<style scoped>
.ops-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 25vh;
}

h2 {
  margin: 0 0 0.65rem;
  font-size: 1.05rem;
  font-weight: 600;
}

.list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.35rem;
}

.row {
  display: grid;
  gap: 0.15rem 0.65rem;
  grid-template-columns: auto 1fr auto;
  align-items: baseline;
  padding: 0.45rem 0.35rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.95rem;
}

.row:last-child {
  border-bottom: none;
}

.row.expense {
  grid-template-columns: auto 1fr auto;
  grid-template-areas:
    "amount category date"
    "desc desc desc";
}

.row.saving {
  grid-template-columns: auto 1fr auto;
  grid-template-areas: "amount kind date";
}

.amount {
  grid-area: amount;
  font-weight: 600;
  white-space: nowrap;
}

.amount.saving {
  color: #1d4ed8;
}

.category {
  grid-area: category;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kind-label {
  grid-area: kind;
  color: #64748b;
  font-size: 0.85rem;
}

.date {
  grid-area: date;
  color: #64748b;
  font-size: 0.85rem;
  white-space: nowrap;
}

.desc {
  grid-area: desc;
  color: #64748b;
  font-size: 0.85rem;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty {
  margin: 0;
  color: #64748b;
}

.more {
  margin-top: 0.65rem;
  width: 100%;
}

@media (min-width: 560px) {
  .row.expense {
    grid-template-columns: 7rem minmax(6rem, 10rem) 7rem 1fr;
    grid-template-areas: "amount category date desc";
    align-items: center;
  }

  .row.saving {
    grid-template-columns: 7rem minmax(6rem, 10rem) 7rem 1fr;
    grid-template-areas: "amount kind date .";
    align-items: center;
  }
}
</style>
