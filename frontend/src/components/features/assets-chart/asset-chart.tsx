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
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

export const description = "A mixed bar chart";

const rawData = [
  { browser: "chrome", visitors: 275 },
  { browser: "safari", visitors: 200 },
  { browser: "firefox", visitors: 187 },
  { browser: "edge", visitors: 173 },
  { browser: "other", visitors: 90 },
];

const chartConfig = {
  visitors: {
    label: "Visitors",
    color: "var(--gray)",
  },
  chrome: {
    label: "Chrome",
    color: "var(--chart-secondary-1)",
  },
  safari: {
    label: "Safari",
    color: "var(--chart-secondary-2)",
  },
  firefox: {
    label: "Firefox",
    color: "var(--chart-secondary-3)",
  },
  edge: {
    label: "Edge",
    color: "var(--chart-secondary-4)",
  },
  other: {
    label: "Other",
    color: "var(--chart-secondary-5)",
  },
} satisfies ChartConfig;

const chartData = rawData
  .slice(0, 5) // garante no máximo 5 itens
  .map((item) => ({
    ...item,
    fill:
      chartConfig[item.browser as keyof typeof chartConfig]?.color ?? "gray",
  }));

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
              right: 16,
            }}
          >
            <YAxis
              dataKey="browser"
              type="category"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) =>
                chartConfig[value as keyof typeof chartConfig]?.label
              }
            />
            <XAxis dataKey="visitors" type="number" hide />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <CartesianGrid horizontal={false} />
            <Bar dataKey="visitors" radius={5} layout="vertical">
              <LabelList
                dataKey="visitors"
                position="right"
                offset={8}
                className="fill-foreground"
                fontSize={12}
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
