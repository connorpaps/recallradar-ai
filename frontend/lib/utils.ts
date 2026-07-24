import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatDate(value?: string | null) {
  if (!value) return "Unknown";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

export function formatScore(value: string | number) {
  return `${Math.round(Number(value) * 100)}%`;
}

export function formatExposure(value: string | number) {
  return `${Math.round(Number(value))}`;
}
