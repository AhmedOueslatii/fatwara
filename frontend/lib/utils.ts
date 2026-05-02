import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTND(value: string | number): string {
  const n = typeof value === "string" ? Number(value) : value;
  return new Intl.NumberFormat("fr-TN", {
    style: "currency",
    currency: "TND",
    minimumFractionDigits: 3,
  }).format(n);
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("fr-TN");
}

const TN_MATRICULE = /^\d{7}[A-Z]\/[A-Z]\/[A-Z]\/\d{3}$/;

export function isValidMatricule(value: string): boolean {
  return TN_MATRICULE.test(value);
}
