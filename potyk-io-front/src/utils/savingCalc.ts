export type RemainderDay = {
  date: string;
  budget: number;
  start_available: number;
  spent: number;
  eod_remainder: number;
  end_balance: number;
  savings: readonly unknown[];
};

export type SavingCalcPart = {
  date: string;
  /** Доступно на день (бюджет минус перенос долга). */
  available: number;
  spent: number;
  /** Плюс остаток или минус долг. */
  amount: number;
};

/** Дневной вклад: плюс остаток или минус долг (проебанный день). */
function daySavingAmount(day: RemainderDay): number {
  if (day.end_balance < 0) return day.end_balance;
  return day.eod_remainder;
}

/** Остатки/долги с даты последнего сейфа включительно (до today).
 * В сумму и округление идут только положительные остатки; долги только в разбивке. */
export function calcSavingFromRemainders(
  days: readonly RemainderDay[],
  today: string,
): { parts: SavingCalcPart[]; sum: number; rounded: number } | null {
  let lastSavingDate: string | null = null;
  for (const d of days) {
    if (d.savings.length > 0 && (lastSavingDate == null || d.date > lastSavingDate)) {
      lastSavingDate = d.date;
    }
  }

  // Дата последнего сейфа включительно: если сейф был 21.11 — остаток/долг 21.11 тоже в разбивке.
  const parts = days
    .filter((d) => d.date < today && (lastSavingDate == null || d.date >= lastSavingDate))
    .map((d) => ({
      date: d.date,
      available: d.start_available,
      spent: d.spent,
      amount: daySavingAmount(d),
    }))
    .filter((p) => p.amount !== 0)
    .slice()
    .sort((a, b) => a.date.localeCompare(b.date));

  if (!parts.length) return null;

  const sum = parts.filter((p) => p.amount > 0).reduce((acc, p) => acc + p.amount, 0);
  let rounded = Math.round(sum / 1000) * 1000;
  if (rounded === 0 && sum > 0) rounded = 1000;
  return { parts, sum, rounded };
}
