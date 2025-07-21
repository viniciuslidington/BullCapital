import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { useMemo, useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export const description = "An interactive area chart";

// --- DADOS MOCKADOS PARA OS 4 ATIVOS ---
const chartData = [
  {
    date: "2024-07-01",
    AAPL: 154.32,
    TSLA: 386.11,
    MSFT: 376.98,
    AMZN: 127.27,
  },
  {
    date: "2024-07-02",
    AAPL: 236.74,
    TSLA: 481.01,
    MSFT: 323.19,
    AMZN: 149.75,
  },
  {
    date: "2024-07-03",
    AAPL: 134.47,
    TSLA: 475.72,
    MSFT: 363.34,
    AMZN: 167.49,
  },
  {
    date: "2024-07-04",
    AAPL: 236.92,
    TSLA: 177.63,
    MSFT: 520.94,
    AMZN: 370.68,
  },
  {
    date: "2024-07-05",
    AAPL: 152.67,
    TSLA: 482.91,
    MSFT: 475.23,
    AMZN: 338.33,
  },
  {
    date: "2024-07-06",
    AAPL: 136.51,
    TSLA: 309.61,
    MSFT: 332.44,
    AMZN: 101.63,
  },
  {
    date: "2024-07-07",
    AAPL: 214.3,
    TSLA: 338.96,
    MSFT: 553.73,
    AMZN: 238.38,
  },
  {
    date: "2024-07-08",
    AAPL: 259.04,
    TSLA: 237.56,
    MSFT: 549.09,
    AMZN: 247.11,
  },
  {
    date: "2024-07-09",
    AAPL: 241.52,
    TSLA: 445.76,
    MSFT: 454.86,
    AMZN: 266.07,
  },
  {
    date: "2024-07-10",
    AAPL: 146.8,
    TSLA: 205.2,
    MSFT: 406.23,
    AMZN: 198.28,
  },
  {
    date: "2024-07-11",
    AAPL: 156.12,
    TSLA: 315.83,
    MSFT: 338.47,
    AMZN: 266.2,
  },
  {
    date: "2024-07-12",
    AAPL: 191.58,
    TSLA: 198.5,
    MSFT: 369.97,
    AMZN: 132.69,
  },
  {
    date: "2024-07-13",
    AAPL: 232.07,
    TSLA: 281.48,
    MSFT: 203.75,
    AMZN: 365.02,
  },
  {
    date: "2024-07-14",
    AAPL: 170.46,
    TSLA: 375.34,
    MSFT: 317.58,
    AMZN: 305.46,
  },
  {
    date: "2024-07-15",
    AAPL: 151.26,
    TSLA: 453.49,
    MSFT: 530.24,
    AMZN: 124.27,
  },
  {
    date: "2024-07-16",
    AAPL: 278.73,
    TSLA: 445.37,
    MSFT: 478.28,
    AMZN: 251.21,
  },
  {
    date: "2024-07-17",
    AAPL: 264.1,
    TSLA: 420.61,
    MSFT: 340.48,
    AMZN: 112.23,
  },
  {
    date: "2024-07-18",
    AAPL: 255.66,
    TSLA: 220.61,
    MSFT: 304.87,
    AMZN: 167.65,
  },
  {
    date: "2024-07-19",
    AAPL: 269.79,
    TSLA: 430.94,
    MSFT: 360.43,
    AMZN: 237.59,
  },
  {
    date: "2024-07-20",
    AAPL: 147.49,
    TSLA: 463.52,
    MSFT: 340.56,
    AMZN: 221.72,
  },
  {
    date: "2024-07-21",
    AAPL: 208.51,
    TSLA: 420.05,
    MSFT: 482.98,
    AMZN: 214.26,
  },
  {
    date: "2024-07-22",
    AAPL: 123.1,
    TSLA: 401.3,
    MSFT: 362.04,
    AMZN: 346.92,
  },
  {
    date: "2024-07-23",
    AAPL: 140.71,
    TSLA: 451.19,
    MSFT: 328.43,
    AMZN: 146.36,
  },
  {
    date: "2024-07-24",
    AAPL: 152.09,
    TSLA: 387.95,
    MSFT: 431.21,
    AMZN: 302.95,
  },
  {
    date: "2024-07-25",
    AAPL: 163.66,
    TSLA: 348.1,
    MSFT: 596.58,
    AMZN: 377.47,
  },
  {
    date: "2024-07-26",
    AAPL: 126.26,
    TSLA: 199.78,
    MSFT: 337.97,
    AMZN: 361.83,
  },
  {
    date: "2024-07-27",
    AAPL: 133.39,
    TSLA: 185.87,
    MSFT: 404.62,
    AMZN: 297.4,
  },
  {
    date: "2024-07-28",
    AAPL: 254.25,
    TSLA: 240.22,
    MSFT: 217.92,
    AMZN: 342.9,
  },
  {
    date: "2024-07-29",
    AAPL: 249.53,
    TSLA: 481.86,
    MSFT: 587.97,
    AMZN: 185.77,
  },
  {
    date: "2024-07-30",
    AAPL: 250.05,
    TSLA: 163.38,
    MSFT: 270.37,
    AMZN: 343.2,
  },
  {
    date: "2024-07-31",
    AAPL: 246.4,
    TSLA: 425.99,
    MSFT: 492.85,
    AMZN: 127.36,
  },
  {
    date: "2024-08-01",
    AAPL: 164.44,
    TSLA: 489.54,
    MSFT: 421.74,
    AMZN: 324.33,
  },
  {
    date: "2024-08-02",
    AAPL: 133.08,
    TSLA: 407.09,
    MSFT: 217.22,
    AMZN: 196.62,
  },
  {
    date: "2024-08-03",
    AAPL: 245.01,
    TSLA: 207.92,
    MSFT: 420.3,
    AMZN: 162.97,
  },
  {
    date: "2024-08-04",
    AAPL: 137.05,
    TSLA: 334.53,
    MSFT: 294.27,
    AMZN: 181.53,
  },
  {
    date: "2024-08-05",
    AAPL: 205.91,
    TSLA: 348.19,
    MSFT: 451.69,
    AMZN: 309.13,
  },
  {
    date: "2024-08-06",
    AAPL: 236.9,
    TSLA: 423.32,
    MSFT: 211.31,
    AMZN: 165.72,
  },
  {
    date: "2024-08-07",
    AAPL: 203.67,
    TSLA: 461.4,
    MSFT: 379.72,
    AMZN: 205.75,
  },
  {
    date: "2024-08-08",
    AAPL: 130.12,
    TSLA: 239.48,
    MSFT: 336.39,
    AMZN: 310.44,
  },
  {
    date: "2024-08-09",
    AAPL: 215.74,
    TSLA: 423.7,
    MSFT: 255.54,
    AMZN: 264.15,
  },
  {
    date: "2024-08-10",
    AAPL: 176.47,
    TSLA: 286.28,
    MSFT: 236.25,
    AMZN: 424.57,
  },
  {
    date: "2024-08-11",
    AAPL: 177.6,
    TSLA: 379.28,
    MSFT: 444.24,
    AMZN: 310.32,
  },
  {
    date: "2024-08-12",
    AAPL: 255.63,
    TSLA: 468.81,
    MSFT: 569.63,
    AMZN: 257.02,
  },
  {
    date: "2024-08-13",
    AAPL: 271.37,
    TSLA: 377.38,
    MSFT: 210.48,
    AMZN: 359.91,
  },
  {
    date: "2024-08-14",
    AAPL: 244.01,
    TSLA: 485.56,
    MSFT: 245.95,
    AMZN: 401.9,
  },
  {
    date: "2024-08-15",
    AAPL: 218.88,
    TSLA: 404.62,
    MSFT: 396.19,
    AMZN: 155.54,
  },
  {
    date: "2024-08-16",
    AAPL: 268.24,
    TSLA: 392.23,
    MSFT: 445.94,
    AMZN: 423.26,
  },
  {
    date: "2024-08-17",
    AAPL: 239.63,
    TSLA: 467.46,
    MSFT: 263.09,
    AMZN: 293.11,
  },
  {
    date: "2024-08-18",
    AAPL: 227.03,
    TSLA: 435.88,
    MSFT: 434.7,
    AMZN: 417.64,
  },
  {
    date: "2024-08-19",
    AAPL: 141.64,
    TSLA: 226.21,
    MSFT: 576.64,
    AMZN: 295.63,
  },
  {
    date: "2024-08-20",
    AAPL: 172.9,
    TSLA: 465.16,
    MSFT: 396.03,
    AMZN: 288.85,
  },
  {
    date: "2024-08-21",
    AAPL: 262.64,
    TSLA: 322.31,
    MSFT: 369.18,
    AMZN: 437.84,
  },
  {
    date: "2024-08-22",
    AAPL: 149.88,
    TSLA: 175.48,
    MSFT: 526.61,
    AMZN: 357.92,
  },
  {
    date: "2024-08-23",
    AAPL: 160.45,
    TSLA: 452.77,
    MSFT: 329.15,
    AMZN: 332.78,
  },
  {
    date: "2024-08-24",
    AAPL: 165.22,
    TSLA: 264.15,
    MSFT: 485.83,
    AMZN: 356.36,
  },
  {
    date: "2024-08-25",
    AAPL: 198.83,
    TSLA: 264.32,
    MSFT: 432.84,
    AMZN: 306.1,
  },
  {
    date: "2024-08-26",
    AAPL: 251.36,
    TSLA: 351.18,
    MSFT: 386.37,
    AMZN: 251.93,
  },
  {
    date: "2024-08-27",
    AAPL: 185.89,
    TSLA: 272.45,
    MSFT: 526.05,
    AMZN: 392.06,
  },
  {
    date: "2024-08-28",
    AAPL: 194.89,
    TSLA: 309.78,
    MSFT: 456.5,
    AMZN: 274.0,
  },
  {
    date: "2024-08-29",
    AAPL: 228.08,
    TSLA: 218.97,
    MSFT: 399.71,
    AMZN: 119.77,
  },
  {
    date: "2024-08-30",
    AAPL: 234.7,
    TSLA: 346.55,
    MSFT: 451.89,
    AMZN: 240.31,
  },
  {
    date: "2024-08-31",
    AAPL: 156.75,
    TSLA: 461.55,
    MSFT: 527.13,
    AMZN: 391.99,
  },
  {
    date: "2024-09-01",
    AAPL: 192.6,
    TSLA: 389.07,
    MSFT: 538.64,
    AMZN: 425.76,
  },
  {
    date: "2024-09-02",
    AAPL: 135.49,
    TSLA: 386.61,
    MSFT: 253.51,
    AMZN: 359.22,
  },
  {
    date: "2024-09-03",
    AAPL: 261.07,
    TSLA: 372.58,
    MSFT: 526.27,
    AMZN: 290.0,
  },
  {
    date: "2024-09-04",
    AAPL: 187.79,
    TSLA: 273.9,
    MSFT: 304.27,
    AMZN: 181.33,
  },
  {
    date: "2024-09-05",
    AAPL: 148.67,
    TSLA: 256.35,
    MSFT: 295.7,
    AMZN: 334.09,
  },
  {
    date: "2024-09-06",
    AAPL: 204.69,
    TSLA: 333.38,
    MSFT: 527.32,
    AMZN: 349.29,
  },
  {
    date: "2024-09-07",
    AAPL: 155.73,
    TSLA: 286.34,
    MSFT: 579.41,
    AMZN: 252.64,
  },
  {
    date: "2024-09-08",
    AAPL: 211.37,
    TSLA: 481.58,
    MSFT: 461.01,
    AMZN: 411.06,
  },
  {
    date: "2024-09-09",
    AAPL: 225.38,
    TSLA: 183.3,
    MSFT: 523.37,
    AMZN: 278.58,
  },
  {
    date: "2024-09-10",
    AAPL: 127.86,
    TSLA: 472.98,
    MSFT: 482.85,
    AMZN: 260.23,
  },
  {
    date: "2024-09-11",
    AAPL: 216.09,
    TSLA: 498.9,
    MSFT: 407.81,
    AMZN: 129.57,
  },
  {
    date: "2024-09-12",
    AAPL: 134.93,
    TSLA: 184.88,
    MSFT: 469.33,
    AMZN: 151.39,
  },
  {
    date: "2024-09-13",
    AAPL: 228.62,
    TSLA: 203.03,
    MSFT: 426.82,
    AMZN: 104.34,
  },
  {
    date: "2024-09-14",
    AAPL: 259.83,
    TSLA: 338.21,
    MSFT: 203.88,
    AMZN: 258.42,
  },
  {
    date: "2024-09-15",
    AAPL: 160.66,
    TSLA: 437.58,
    MSFT: 540.45,
    AMZN: 379.26,
  },
  {
    date: "2024-09-16",
    AAPL: 157.7,
    TSLA: 345.68,
    MSFT: 378.12,
    AMZN: 228.91,
  },
  {
    date: "2024-09-17",
    AAPL: 164.98,
    TSLA: 279.92,
    MSFT: 284.12,
    AMZN: 125.82,
  },
  {
    date: "2024-09-18",
    AAPL: 166.38,
    TSLA: 263.63,
    MSFT: 534.61,
    AMZN: 437.66,
  },
  {
    date: "2024-09-19",
    AAPL: 168.18,
    TSLA: 316.37,
    MSFT: 548.88,
    AMZN: 323.36,
  },
  {
    date: "2024-09-20",
    AAPL: 155.81,
    TSLA: 284.63,
    MSFT: 542.79,
    AMZN: 298.93,
  },
  {
    date: "2024-09-21",
    AAPL: 233.69,
    TSLA: 379.52,
    MSFT: 594.59,
    AMZN: 377.28,
  },
  {
    date: "2024-09-22",
    AAPL: 249.63,
    TSLA: 471.96,
    MSFT: 539.14,
    AMZN: 377.88,
  },
  {
    date: "2024-09-23",
    AAPL: 257.03,
    TSLA: 349.24,
    MSFT: 302.54,
    AMZN: 336.08,
  },
  {
    date: "2024-09-24",
    AAPL: 220.27,
    TSLA: 468.13,
    MSFT: 273.49,
    AMZN: 158.62,
  },
  {
    date: "2024-09-25",
    AAPL: 251.08,
    TSLA: 437.95,
    MSFT: 220.55,
    AMZN: 247.44,
  },
  {
    date: "2024-09-26",
    AAPL: 258.49,
    TSLA: 470.04,
    MSFT: 484.13,
    AMZN: 134.03,
  },
  {
    date: "2024-09-27",
    AAPL: 135.32,
    TSLA: 243.14,
    MSFT: 563.69,
    AMZN: 233.79,
  },
  {
    date: "2024-09-28",
    AAPL: 147.62,
    TSLA: 217.12,
    MSFT: 503.14,
    AMZN: 248.01,
  },
];

// --- CONFIGURAÇÃO DO GRÁFICO PARA OS 4 ATIVOS ---
const chartConfig = {
  // Chave 'visitors' ou 'Preço' pode ser usada como um label genérico se necessário
  visitors: { label: "Preço" },
  AAPL: { label: "AAPL", color: "hsl(var(--chart-1))" },
  TSLA: { label: "TSLA", color: "hsl(var(--chart-2))" },
  MSFT: { label: "MSFT", color: "hsl(var(--chart-3))" },
  AMZN: { label: "AMZN", color: "hsl(var(--chart-4))" },
} satisfies ChartConfig;

export function MarketsChart() {
  const [timeRange, setTimeRange] = useState("30d");

  // A lógica de filtragem foi corrigida aqui
  const filteredData = useMemo(() => {
    // Pega a última data dos seus dados como referência
    const lastDataPoint = chartData[chartData.length - 1];
    if (!lastDataPoint) return [];

    const referenceDate = new Date(lastDataPoint.date);

    let daysToSubtract = 90; // Valor padrão
    if (timeRange === "30d") {
      daysToSubtract = 30;
    } else if (timeRange === "7d") {
      daysToSubtract = 7;
    } else if (timeRange === "total") {
      daysToSubtract = chartData.length;
    } else if (timeRange === "1y") {
      daysToSubtract = 365;
    } else if (timeRange === "1d") {
      daysToSubtract = 1;
    }

    const startDate = new Date(referenceDate);
    startDate.setDate(startDate.getDate() - daysToSubtract);

    return chartData.filter((item) => new Date(item.date) >= startDate);
  }, [timeRange]); // Adicionado useMemo para performance

  return (
    <Card className="pt-0">
      <CardHeader className="flex items-center gap-2 space-y-0 border-b py-5 sm:flex-row">
        <div className="grid flex-1 gap-1">
          <CardTitle>Mercado EUA</CardTitle>
          <CardDescription>Variação de preço</CardDescription>
        </div>
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger
            className="w-[160px] rounded-lg sm:ml-auto sm:flex"
            aria-label="Select a value"
          >
            <SelectValue placeholder="Last 3 months" />
          </SelectTrigger>
          <SelectContent className="rounded-xl">
            {/* Mantendo os valores originais para 90, 30 e 7 dias */}
            <SelectItem value="total" className="rounded-lg">
              Total
            </SelectItem>
            <SelectItem value="1y" className="rounded-lg">
              Últimos 365 dias
            </SelectItem>
            <SelectItem value="90d" className="rounded-lg">
              Últimos 90 dias
            </SelectItem>
            <SelectItem value="30d" className="rounded-lg">
              Últimos 30 dias
            </SelectItem>
            <SelectItem value="7d" className="rounded-lg">
              Últimos 7 dias
            </SelectItem>
            <SelectItem value="1d" className="rounded-lg">
              Hoje
            </SelectItem>
          </SelectContent>
        </Select>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-[250px] w-full"
        >
          <AreaChart data={filteredData}>
            <defs>
              <linearGradient id="fillAAPL" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--chart-1)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--chart-1)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient id="fillTSLA" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--chart-2)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--chart-2)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient id="fillMSFT" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--chart-3)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--chart-3)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient id="fillAMZN" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--chart-4)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--chart-4)"
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
              tickFormatter={(value) => {
                const date = new Date(value);
                return date.toLocaleDateString("pt-BR", {
                  month: "short",
                  day: "numeric",
                });
              }}
            />
            {/* O YAxis se ajustará automaticamente aos valores */}
            <YAxis />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="dot" />}
            />
            {/* Atenção: `stackId="a"` soma os valores, o que não é ideal para comparação.
                Para uma comparação real, remova o stackId e considere usar <LineChart> */}
            <Area
              dataKey="AAPL"
              type="natural"
              fill="url(#fillAAPL)"
              stroke="var(--chart-1)"
              stackId="a"
            />
            <Area
              dataKey="TSLA"
              type="natural"
              fill="url(#fillTSLA)"
              stroke="var(--chart-2)"
              stackId="a"
            />
            <Area
              dataKey="MSFT"
              type="natural"
              fill="url(#fillMSFT)"
              stroke="var(--chart-3)"
              stackId="a"
            />
            <Area
              dataKey="AMZN"
              type="natural"
              fill="url(#fillAMZN)"
              stroke="var(--chart-4)"
              stackId="a"
            />
            <ChartLegend content={<ChartLegendContent />} />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
