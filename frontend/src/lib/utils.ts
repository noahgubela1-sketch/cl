import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatMinutes(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

export function formatPageCount(eighths: number): string {
  const full = Math.floor(eighths);
  const rem = Math.round((eighths - full) * 8);
  if (rem === 0) return `${full}`;
  if (full === 0) return `${rem}/8`;
  return `${full} ${rem}/8`;
}
