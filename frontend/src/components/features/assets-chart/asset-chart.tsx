import { TrendingUp } from "lucide-react";
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
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { generateChartDataAndConfig } from "@/lib/utils";

export const description = "A mixed bar chart";

const rawData = [
  { ticker: "AAPL", roe: 1.2 },
  { ticker: "MSFT", roe: 1.1 },
  { ticker: "TSLA", roe: 0.9 },
  { ticker: "TSLA", roe: 0.9 },
  { ticker: "TSLA", roe: 0.9 },
  { ticker: "TSLA", roe: 0.9 },
];

const { chartData, chartConfig } = generateChartDataAndConfig(rawData, "roe", [
  "var(--chart-secondary-1)",
  "var(--chart-secondary-2)",
  "var(--chart-secondary-3)",
  "var(--chart-secondary-4)",
  "var(--chart-secondary-5)",
]);

console.log(chartData, chartConfig);
export function AssetChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Bar Chart - Mixed</CardTitle>
        <CardDescription>January - June 2024</CardDescription>
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
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex gap-2 leading-none font-medium">
          Trending up by 5.2% this month <TrendingUp className="h-4 w-4" />
        </div>
        <div className="text-muted-foreground leading-none">
          Showing total visitors for the last 6 months
        </div>
      </CardFooter>
    </Card>
  );
}
