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

type StockData = {
  ticker: string;
  [key: string]: number | string;
};

export function generateChartDataAndConfig(
  rawData: StockData[],
  selectedIndex: string,
  colors: string[],
) {
  const chartData = rawData.slice(0, colors.length).map((item, i) => ({
    name: item.ticker,
    value: item[selectedIndex],
    fill: colors[i % colors.length],
  }));

  const chartConfig = rawData.slice(0, colors.length).reduce(
    (acc, item, i) => {
      acc[item.ticker] = {
        label: item.ticker,
        color: colors[i % colors.length],
      };
      return acc;
    },
    {} as Record<string, { label: string; color: string }>,
  );

  return { chartData, chartConfig };
}
