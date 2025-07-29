import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function capitalizeFirstLetter(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

export function formatNumber(valor: number) {
  const abs = Math.abs(valor);

  let base = 0;
  let sufixo;

  if (abs >= 1e12) {
    base = valor / 1e12;
    sufixo = " tri";
  } else if (abs >= 1e9) {
    base = valor / 1e9;
    sufixo = " bi";
  } else if (abs >= 1e6) {
    base = valor / 1e6;
    sufixo = " mi";
  } else if (abs >= 1e3) {
    base = valor / 1e3;
    sufixo = " mil";
  } else {
    return valor.toLocaleString("pt-BR"); // número pequeno, sem sufixo
  }

  return `${base.toLocaleString("pt-BR", {
    minimumFractionDigits: base >= 100 ? 0 : 2,
    maximumFractionDigits: 2,
  })}${sufixo}`;
}

// Helper para formatar o preço como moeda (ex: $187.45)
export const formatPrice = (price: number, currency: string) => {
  return price.toLocaleString("pt-BR", {
    style: "currency",
    currency: currency,
  });
};

export const formatDate = (rawDate: string) => {
  return new Date(rawDate).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZoneName: "short",
  });
};

// Helper para formatar a variação, adicionando o sinal de '+'
export const formatChange = (change: number, percentage = true) => {
  const sign = change > 0 ? "+" : "";
  return `${sign}${change.toFixed(2)}${percentage ? "%" : ""}`;
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

type ChartConfigEntry = {
  label: string;
  color?: string;
};

type ChartConfig = Record<string, ChartConfigEntry>;

export function generateMarketChartConfig(
  chartData: { [key: string]: number | string }[],
  options?: { includePreco?: boolean },
): ChartConfig {
  if (!chartData || chartData.length === 0) return {};

  const keys = Object.keys(chartData[0]).filter((key) => key !== "date");

  const config: ChartConfig = Object.fromEntries(
    keys.map((key, index) => [
      key,
      {
        label: key,
        color: `var(--chart-${index + 1})`,
      },
    ]),
  );

  if (options?.includePreco) {
    config["preco"] = { label: "Preço" };
  }

  return config;
}
