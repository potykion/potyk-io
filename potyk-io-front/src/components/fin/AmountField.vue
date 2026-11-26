<script setup lang="ts">
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import { computed, onBeforeUnmount, ref } from "vue";
import { evalAmountExpression } from "@/utils/calc";

const amount = defineModel<number | null>("amount", { required: true });
const formula = defineModel<string>("formula", { default: "" });

const props = defineProps<{
  allowFormula?: boolean;
  /** Кнопка 1к. По умолчанию — только без allowFormula. */
  showRound?: boolean;
  large?: boolean;
  placeholder?: string;
  inputId?: string;
}>();

const canRound = computed(() => props.showRound ?? !props.allowFormula);

const showCalc = ref(false);
const calcInput = ref("");
let formulaTimer: ReturnType<typeof setTimeout> | null = null;

onBeforeUnmount(() => {
  if (formulaTimer) clearTimeout(formulaTimer);
});

/** Сворачивание формулы в число — только после ручного ввода, не при программной подстановке. */
function scheduleCollapse(): void {
  if (!props.allowFormula) return;
  if (formulaTimer) clearTimeout(formulaTimer);
  formulaTimer = setTimeout(() => {
    const value = formula.value;
    if (!value) return;
    const result = evalAmountExpression(value);
    if (result != null) {
      amount.value = result;
      formula.value = String(result);
    }
  }, 1000);
}

function onAmountInput(event: Event): void {
  const raw = (event.target as HTMLInputElement).value;
  if (props.allowFormula) {
    formula.value = raw;
    amount.value = evalAmountExpression(raw);
    scheduleCollapse();
    return;
  }
  const n = Number.parseInt(raw.replace(/\s/g, ""), 10);
  amount.value = Number.isFinite(n) ? n : null;
}

function applyCalc(): void {
  const result = evalAmountExpression(calcInput.value);
  if (result != null) {
    amount.value = result;
    formula.value = String(result);
    showCalc.value = false;
  }
}

function roundToThousand(): void {
  if (amount.value == null) return;
  amount.value = Math.round(amount.value / 1000) * 1000 || 1000;
  formula.value = String(amount.value);
}
</script>

<template>
  <div class="amount-field">
    <div class="amount-row">
      <InputText
        :id="inputId"
        class="amount-input"
        :class="{ large }"
        :placeholder="placeholder"
        :model-value="
          allowFormula
            ? formula || (amount != null ? String(amount) : '')
            : amount != null
              ? String(amount)
              : ''
        "
        inputmode="decimal"
        @input="onAmountInput"
      />
      <Button
        v-if="!allowFormula"
        type="button"
        text
        rounded
        label="🧮"
        aria-label="Калькулятор"
        @click="showCalc = !showCalc"
      />
      <Button
        v-if="canRound"
        type="button"
        text
        rounded
        label="1к"
        aria-label="Округлить до тысячи"
        @click="roundToThousand"
      />
    </div>
    <div v-if="showCalc && !allowFormula" class="calc-panel">
      <InputText v-model="calcInput" placeholder="123+456" aria-label="Формула" />
      <Button type="button" label="=" @click="applyCalc" />
    </div>
  </div>
</template>

<style scoped>
.amount-row {
  display: flex;
  gap: 0.35rem;
  align-items: center;
}

.amount-input {
  flex: 1;
  min-width: 0;
}

.amount-input.large {
  font-size: 1.5rem;
  padding: 0.75rem 0.9rem;
  font-weight: 600;
}

.calc-panel {
  display: flex;
  gap: 0.35rem;
  margin-top: 0.4rem;
}
</style>
