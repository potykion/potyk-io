export type RemainderDay = {
  date: string;
  eod_remainder: number;
  savings: readonly unknown[];
};

export type SavingCalcPart = {
  date: string;
  amount: number;
};

/** Остатки с даты последнего сейфа включительно (до today), сумма и округление до 1к. */
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

  // Дата последнего сейфа включительно: если сейф был 21.11 — остаток/траты 21.11 тоже в расчёте.
  const parts = days
    .filter(
      (d) =>
        d.date < today &&
        (lastSavingDate == null || d.date >= lastSavingDate) &&
        d.eod_remainder > 0,
    )
    .slice()
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((d) => ({ date: d.date, amount: d.eod_remainder }));

  if (!parts.length) return null;

  const sum = parts.reduce((acc, p) => acc + p.amount, 0);
  const rounded = Math.round(sum / 1000) * 1000 || 1000;
  return { parts, sum, rounded };
}
