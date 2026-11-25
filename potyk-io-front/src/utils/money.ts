export function formatRub(value: number): string {
  return `${Math.round(value).toLocaleString("ru-RU")} ₽`;
}

const WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"] as const;

export function formatDayLabel(isoDate: string, today?: string): string {
  const d = new Date(`${isoDate}T12:00:00`);
  if (Number.isNaN(d.getTime())) {
    return isoDate;
  }
  const weekday = WEEKDAYS[d.getDay() === 0 ? 6 : d.getDay() - 1];
  const todayMark = today && isoDate === today ? " · сегодня" : "";
  return `${isoDate} · ${weekday}${todayMark}`;
}

export function pct(part: number, whole: number): number {
  if (!whole) return 0;
  return Math.round((part / whole) * 100);
}
