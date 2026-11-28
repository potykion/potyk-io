<script setup lang="ts">
import Accordion from "primevue/accordion";
import AccordionContent from "primevue/accordioncontent";
import AccordionHeader from "primevue/accordionheader";
import AccordionPanel from "primevue/accordionpanel";
import Button from "primevue/button";
import Checkbox from "primevue/checkbox";
import { computed, ref, watch } from "vue";
import type { FinDay } from "@/api/fin";
import { formatDayLabel, formatRub } from "@/utils/money";

const props = defineProps<{
  days: FinDay[];
  today: string;
  pickMode: boolean;
  selectedRemainders: string[];
  busy?: boolean;
}>();

const emit = defineEmits<{
  editExpense: [id: number];
  deleteExpense: [id: number];
  editSaving: [id: number];
  deleteSaving: [id: number];
  toggleClosed: [date: string, closed: boolean];
  addExpenseDate: [date: string];
  addSavingFromRemainder: [amount: number, date: string];
  toggleRemainder: [date: string];
}>();

const openPanels = ref<string[]>([]);

watch(
  () => props.days,
  (days) => {
    if (!openPanels.value.length && days.length) {
      openPanels.value = days
        .filter((d) => !d.closed)
        .slice(0, 3)
        .map((d) => d.date);
      if (!openPanels.value.length) openPanels.value = [days[0].date];
    }
  },
  { immediate: true },
);

const selectedSet = computed(() => new Set(props.selectedRemainders));

function balanceClass(value: number): string {
  if (value < 0) return "bad";
  if (value > 0) return "ok";
  return "";
}
</script>

<template>
  <section>
    <h2>Лента</h2>
    <p v-if="!days.length" class="empty">Пока нет трат — добавь первую.</p>

    <Accordion v-else v-model:value="openPanels" multiple>
      <AccordionPanel v-for="day in days" :key="day.date" :value="day.date">
        <AccordionHeader>
          <div class="day-head">
            <div>
              <div>{{ formatDayLabel(day.date, today) }}</div>
              <div class="meta">
                старт {{ formatRub(day.start_available) }}
                <template v-if="day.carry_in"
                  >· долг вчера −{{ formatRub(day.carry_in) }}</template
                >
              </div>
            </div>
            <div class="badges">
              <span class="badge">потрачено {{ formatRub(day.spent) }}</span>
              <Button
                v-if="!day.closed"
                type="button"
                size="small"
                text
                rounded
                icon="pi pi-plus"
                aria-label="Добавить трату на день"
                @click.stop="emit('addExpenseDate', day.date)"
              />
              <span
                v-if="day.end_balance < 0"
                class="badge bad"
                >долг {{ formatRub(day.carry_out) }}</span
              >
              <button
                v-else
                type="button"
                class="badge ok remainder"
                :class="{
                  pickable: pickMode && day.date < today,
                  selected: selectedSet.has(day.date),
                }"
                @click.stop="
                  pickMode && day.date < today
                    ? emit('toggleRemainder', day.date)
                    : undefined
                "
              >
                остаток {{ formatRub(day.eod_remainder) }}
              </button>
              <Button
                v-if="!day.closed && day.end_balance >= 0"
                type="button"
                size="small"
                text
                rounded
                icon="pi pi-wallet"
                aria-label="Сейв с остатка"
                @click.stop="emit('addSavingFromRemainder', day.eod_remainder, day.date)"
              />
              <span v-if="day.saved" class="badge saved"
                >сейв {{ formatRub(day.saved) }}</span
              >
            </div>
          </div>
        </AccordionHeader>
        <AccordionContent>
          <div v-if="day.expenses.length" class="table-wrap">
            <table class="table table--expenses">
              <thead>
                <tr>
                  <th>Сумма</th>
                  <th>Категория</th>
                  <th>Описание</th>
                  <th>Баланс</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="e in day.expenses"
                  :key="e.id"
                  :class="{ optional: e.optional }"
                >
                  <td>{{ formatRub(e.amount) }}</td>
                  <td>{{ e.category }}</td>
                  <td class="muted">{{ e.description || "—" }}</td>
                  <td :class="balanceClass(e.running_balance ?? 0)">
                    {{ formatRub(e.running_balance ?? 0) }}
                  </td>
                  <td v-if="!day.closed" class="actions">
                    <Button
                      type="button"
                      icon="pi pi-pencil"
                      text
                      rounded
                      size="small"
                      @click="emit('editExpense', e.id)"
                    />
                    <Button
                      type="button"
                      icon="pi pi-times"
                      text
                      rounded
                      size="small"
                      severity="danger"
                      :disabled="busy"
                      @click="emit('deleteExpense', e.id)"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty">Трат нет</p>

          <div v-if="day.savings.length" class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Сейв</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in day.savings" :key="s.id">
                  <td>
                    {{ formatRub(s.amount) }}
                    <span v-if="s.note" class="muted"> · {{ s.note }}</span>
                  </td>
                  <td v-if="!day.closed" class="actions">
                    <Button
                      type="button"
                      icon="pi pi-pencil"
                      text
                      rounded
                      size="small"
                      @click="emit('editSaving', s.id)"
                    />
                    <Button
                      type="button"
                      icon="pi pi-times"
                      text
                      rounded
                      size="small"
                      severity="danger"
                      :disabled="busy"
                      @click="emit('deleteSaving', s.id)"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <label class="close-day">
            <Checkbox
              :model-value="day.closed"
              binary
              :disabled="busy"
              @update:model-value="(v) => emit('toggleClosed', day.date, Boolean(v))"
            />
            <span>День закрыт</span>
          </label>
        </AccordionContent>
      </AccordionPanel>
    </Accordion>
  </section>
</template>

<style scoped>
h2 {
  margin: 1.25rem 0 0.75rem;
  font-size: 1.25rem;
}

.day-head {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  width: 100%;
  padding-right: 0.5rem;
}

.meta {
  color: #64748b;
  font-size: 0.85rem;
}

.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
}

.badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.15rem 0.55rem;
  font-size: 0.8rem;
  background: #e2e8f0;
  border: 1px solid transparent;
}

.badge.ok {
  background: #dcfce7;
}

.badge.bad {
  background: #fee2e2;
}

.badge.saved {
  background: #dbeafe;
}

.remainder {
  cursor: default;
  font: inherit;
}

.remainder.pickable {
  cursor: pointer;
}

.remainder.selected {
  border-color: #0f172a;
  box-shadow: 0 0 0 1px #0f172a;
}

.table-wrap {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin-bottom: 0.75rem;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.table--expenses {
  min-width: 28rem;
}

.table th,
.table td {
  text-align: left;
  padding: 0.4rem 0.35rem;
  border-bottom: 1px solid #e2e8f0;
}

.muted {
  color: #64748b;
}

.optional {
  opacity: 0.65;
}

.ok {
  color: #15803d;
}

.bad {
  color: #b91c1c;
}

.actions {
  white-space: nowrap;
}

.close-day {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.empty {
  color: #64748b;
}

@media (min-width: 720px) {
  .day-head {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
