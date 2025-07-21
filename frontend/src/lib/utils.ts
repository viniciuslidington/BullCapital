import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Helper para formatar o preço como moeda (ex: $187.45)
export const formatPrice = (price: number, currency: string) => {
  return price.toLocaleString("pt-BR", {
    style: "currency",
    currency: currency,
  });
};

// Helper para formatar a variação, adicionando o sinal de '+'
export const formatChange = (change: number) => {
  const sign = change > 0 ? "+" : "";
  return `${sign}${change.toFixed(2)}%`;
};
