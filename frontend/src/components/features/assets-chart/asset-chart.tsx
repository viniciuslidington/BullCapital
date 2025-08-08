import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  XAxis,
  YAxis,
} from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { generateChartDataAndConfig } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";

import { QuestionMark } from "@/components/ui/question-mark";
import type { IndexesType } from "@/types/assets";
import { indexesData } from "@/data/indexes-data";

const rawData = [
  {
    ticker: "WEGE3",
    roe: 0.32,
  },
  {
    ticker: "PETR4",
    roe: 0.29,
  },
  {
    ticker: "BBAS3",
    roe: 0.22,
  },
  {
    ticker: "ITUB4",
    roe: 0.21,
  },

  {
    ticker: "VALE3",
    roe: 0.18,
  },
];

const { chartData, chartConfig } = generateChartDataAndConfig(rawData, "roe", [
  "var(--chart-secondary-1)",
  "var(--chart-secondary-2)",
  "var(--chart-secondary-3)",
  "var(--chart-secondary-4)",
  "var(--chart-secondary-5)",
]);

export function AssetChart() {
  const [dataIndex, setDataIndex] = useState<IndexesType>("roe");

  return (
    <div className="flex flex-col gap-2">
      <p className="text-muted-foreground dark:text-foreground flex h-9 items-center font-semibold">
        COMPARAR ATIVOS
      </p>
      <Card className="bg-card/60 pt-0">
        <CardHeader className="flex items-center gap-2 space-y-0 border-b py-5 sm:flex-row">
          <div className="grid flex-1 gap-1">
            <IndexTitle
              title={indexesData[dataIndex].title}
              dataIndex={dataIndex}
            />
            <CardDescription>Julho 2025</CardDescription>
          </div>
          <Button variant="link" className="text-primary cursor-pointer">
            Editar Ativos
          </Button>
          <SelectIndex dataIndex={dataIndex} setDataIndex={setDataIndex} />
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={chartConfig}
            className="h-[250px] w-full max-w-[1000px]"
          >
            <BarChart
              accessibilityLayer
              data={chartData}
              layout="vertical"
              margin={{
                right: 32,
              }}
            >
              <YAxis
                dataKey="name"
                type="category"
                tickLine={false}
                tickMargin={10}
                axisLine={false}
              />
              <XAxis dataKey="value" type="number" hide />
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent indicator="line" />}
              />
              <CartesianGrid horizontal={false} />
              <Bar dataKey="value" radius={5} layout="vertical">
                <LabelList
                  dataKey="value"
                  position="right"
                  offset={8}
                  className="fill-foreground"
                  fontSize={12}
                  fontWeight={600}
                />
              </Bar>
            </BarChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  );
}

function SelectIndex({
  dataIndex,
  setDataIndex,
}: {
  dataIndex: string;
  setDataIndex: React.Dispatch<React.SetStateAction<IndexesType>>;
}) {
  return (
    <Select
      value={dataIndex}
      onValueChange={(value) => setDataIndex(value as IndexesType)}
    >
      <SelectTrigger
        className="w-[160px] rounded-lg sm:ml-auto sm:flex"
        aria-label="Select a value"
      >
        <SelectValue placeholder="Selecionar índices" />
      </SelectTrigger>
      <SelectContent className="rounded-xl" align="end">
        <SelectItem value="price" className="rounded-lg">
          Preço
        </SelectItem>
        <SelectItem value="priceChangePercent" className="rounded-lg">
          Variação
        </SelectItem>
        <SelectItem value="roe" className="rounded-lg">
          ROE
        </SelectItem>
        <SelectItem value="dy" className="rounded-lg">
          Dividend Yield
        </SelectItem>
        <SelectItem value="yearHigh" className="rounded-lg">
          Max 52s
        </SelectItem>
        <SelectItem value="marketCap" className="rounded-lg">
          Valor de mercado
        </SelectItem>
        <SelectItem value="peRatio" className="rounded-lg">
          {"Índice P/L (Ações/ETFs/BDRs)"}
        </SelectItem>
        <SelectItem value="netMargin" className="rounded-lg">
          {"Margem Líquida (Ações/BDRs)"}
        </SelectItem>
        <SelectItem value="pFfo" className="rounded-lg">
          {"P/FFO / (FIIs)"}
        </SelectItem>
        <SelectItem value="pVp" className="rounded-lg">
          {"P/VP (FIIs)"}
        </SelectItem>
      </SelectContent>
    </Select>
  );
}

function IndexTitle({
  title,
  dataIndex,
}: {
  title?: string;
  dataIndex: IndexesType;
}) {
  return (
    <CardTitle className="flex items-center gap-1.5">
      {title}
      <QuestionMark dataType="indexes" dataIndex={dataIndex} delay={100} />
    </CardTitle>
  );
}
