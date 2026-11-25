<script setup lang="ts">
import Accordion from "primevue/accordion";
import AccordionContent from "primevue/accordioncontent";
import AccordionHeader from "primevue/accordionheader";
import AccordionPanel from "primevue/accordionpanel";
import Button from "primevue/button";
import DatePicker from "primevue/datepicker";
import { computed, ref, watch } from "vue";
import type { FinState } from "@/api/fin";
import { formatRub, pct } from "@/utils/money";

const props = defineProps<{
  stats: FinState["stats"];
}>();

const emit = defineEmits<{
  change: [from: string, to: string];
}>();

const fromDate = ref<Date | null>(null);
const toDate = ref<Date | null>(null);
const openCats = ref<string[]>([]);

watch(
  () => [props.stats.from, props.stats.to],
  () => {
    fromDate.value = new Date(`${props.stats.from}T12:00:00`);
    toDate.value = new Date(`${props.stats.to}T12:00:00`);
  },
  { immediate: true },
);

const hasCats = computed(() => props.stats.categories.length > 0);

function iso(d: Date | null): string | null {
  if (!d) return null;
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function show(): void {
  const from = iso(fromDate.value);
  const to = iso(toDate.value);
  if (from && to) emit("change", from, to);
}

function goPrev(): void {
  emit("change", props.stats.prev_from, props.stats.prev_to);
}

function goNext(): void {
  if (props.stats.next_from && props.stats.next_to) {
    emit("change", props.stats.next_from, props.stats.next_to);
  }
}
</script>

<template>
  <details class="panel" open>
    <summary>Статистика</summary>
    <div class="period">
      <label>
        <span>С</span>
        <DatePicker v-model="fromDate" date-format="yy-mm-dd" show-icon />
      </label>
      <label>
        <span>По</span>
        <DatePicker v-model="toDate" date-format="yy-mm-dd" show-icon />
      </label>
      <Button type="button" label="Показать" severity="secondary" @click="show" />
      <div class="months">
        <Button
          type="button"
          size="small"
          severity="secondary"
          :label="`← ${stats.prev_month_label}`"
          @click="goPrev"
        />
        <Button
          v-if="stats.next_from && stats.next_month_label"
          type="button"
          size="small"
          severity="secondary"
          :label="`${stats.next_month_label} →`"
          @click="goNext"
        />
      </div>
    </div>

    <template v-if="hasCats">
      <table class="totals">
        <tbody>
          <tr>
            <th>Итого</th>
            <td>
              {{ formatRub(stats.total)
              }}<template v-if="stats.expenses_plus_saves">
                ({{ pct(stats.total, stats.expenses_plus_saves) }}%)</template
              >
            </td>
          </tr>
          <tr>
            <th>Сейвы</th>
            <td>
              {{ formatRub(stats.saved_total)
              }}<template v-if="stats.expenses_plus_saves">
                ({{ pct(stats.saved_total, stats.expenses_plus_saves) }}%)</template
              >
            </td>
          </tr>
          <tr>
            <th>Расход и сейвы</th>
            <td>{{ formatRub(stats.expenses_plus_saves) }}</td>
          </tr>
        </tbody>
      </table>

      <Accordion v-model:value="openCats" multiple>
        <AccordionPanel
          v-for="row in stats.categories"
          :key="row.category"
          :value="row.category"
        >
          <AccordionHeader>
            <span class="cat-head">
              <span class="cat-bar" :style="{ width: `${pct(row.total, stats.total)}%` }" />
              <span class="cat-lead">
                <strong>{{ row.category }}</strong>
                <span class="muted"
                  >{{ row.count }} оп. · ср. {{ formatRub(row.avg) }}</span
                >
              </span>
              <span
                >{{ formatRub(row.total) }} ({{ pct(row.total, stats.total) }}%)</span
              >
            </span>
          </AccordionHeader>
          <AccordionContent>
            <table class="ops">
              <thead>
                <tr>
                  <th>Дата</th>
                  <th>Сумма</th>
                  <th>Комментарий</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in row.expenses" :key="e.id">
                  <td>{{ e.date }}</td>
                  <td>{{ formatRub(e.amount) }}</td>
                  <td class="muted">{{ e.description || "—" }}</td>
                </tr>
              </tbody>
            </table>
          </AccordionContent>
        </AccordionPanel>
      </Accordion>
    </template>
    <template v-else>
      <p class="empty">За выбранный период трат нет</p>
      <table v-if="stats.saved_total" class="totals">
        <tbody>
          <tr>
            <th>Сейвы</th>
            <td>{{ formatRub(stats.saved_total) }}</td>
          </tr>
          <tr>
            <th>Расход и сейвы</th>
            <td>{{ formatRub(stats.expenses_plus_saves) }}</td>
          </tr>
        </tbody>
      </table>
    </template>
  </details>
</template>

<style scoped>
.panel {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 0.75rem;
}

summary {
  cursor: pointer;
  font-weight: 600;
}

.period {
  display: grid;
  gap: 0.6rem;
  margin: 0.75rem 0;
}

.period label {
  display: grid;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: #64748b;
}

.months {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.totals,
.ops {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 0.75rem;
}

.totals th,
.totals td,
.ops th,
.ops td {
  text-align: left;
  padding: 0.35rem 0.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.cat-head {
  position: relative;
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  width: 100%;
  align-items: center;
}

.cat-bar {
  position: absolute;
  inset: 0 auto 0 0;
  background: #e2e8f0;
  border-radius: 0.25rem;
  z-index: 0;
}

.cat-lead,
.cat-head > span:last-child {
  position: relative;
  z-index: 1;
}

.cat-lead {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.muted {
  color: #64748b;
}

.empty {
  color: #64748b;
}
</style>
