import { useMarketOverview } from "@/hooks/queries/usemarketoverview";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from "@/components/ui/carousel";
import { useNavigate } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowDown, ArrowUp, Minus } from "lucide-react";

const response = {
  lastUpdated: "2025-07-18T14:43:00-03:00",
  cards: [
    {
      ticker: "IBOV",
      name: "Ibovespa",
      type: "index",
      value: 136362.5,
      unit: "pts",
      changePercent: -0.81,
    },
    {
      ticker: "IFIX",
      name: "IFIX",
      type: "index",
      value: 3420.1,
      unit: "pts",
      changePercent: 0.12,
    },
    {
      ticker: "SMLL",
      name: "SMLL",
      type: "index",
      value: 2250.75,
      unit: "pts",
      changePercent: -0.25,
    },
    {
      ticker: "CDI",
      name: "CDI 12m",
      type: "fixed_income",
      value: 12.14,
      unit: "%",
      changePercent: 1.09,
    },
    {
      ticker: "SPX",
      name: "S&P 500",
      type: "index",
      value: 5635.25,
      unit: "pts",
      changePercent: 0.27,
    },
    {
      ticker: "^IXIC",
      name: "Nasdaq",
      type: "index",
      value: 18250.15,
      unit: "pts",
      changePercent: 0.42,
    },
    {
      ticker: "USDBRL",
      name: "USD",
      type: "currency",
      value: 5.55,
      unit: "R$",
      changePercent: -0.18,
    },
  ],
};

export function MarketOverview() {
  const {
    data: response,
    isLoading,
    isFetching,
    error,
  } = useMarketOverview("brasil");
  const navigate = useNavigate();

  return (
    <Carousel opts={{ dragFree: true }}>
      <CarouselContent className="select-none">
        {isLoading
          ? Array.from({ length: 6 }).map((_, idx) => (
              <CarouselItem
                key={idx}
                className="border-border bg-card ml-4 flex w-auto shrink-0 grow-0 basis-auto cursor-pointer rounded-[12px] border p-2 shadow-sm transition-all duration-200 ease-in-out hover:shadow-md"
              >
                <div className="flex items-end justify-between gap-5">
                  <span className="flex flex-col gap-2">
                    <Skeleton className="h-3 w-20"></Skeleton>
                    <Skeleton className="h-2 w-10"></Skeleton>
                  </span>
                  <Skeleton className="h-10 w-16"></Skeleton>
                </div>
              </CarouselItem>
            ))
          : response?.data?.map((item) => (
              <CarouselItem
                className="border-border bg-card ml-4 flex w-auto shrink-0 grow-0 basis-auto cursor-pointer rounded-[12px] border p-2 shadow-sm transition-all duration-200 ease-in-out hover:shadow-md"
                onClick={() => navigate(item.symbol)}
              >
                <div className="flex items-end justify-between gap-3">
                  <span className="flex flex-col">
                    <p className="text-foreground/85 max-w-22 overflow-hidden text-sm font-medium text-ellipsis whitespace-nowrap">
                      {item.name}
                    </p>
                    <p
                      className={`text-xs ${isFetching ? "text-muted-foreground/70" : "text-muted-foreground"}`}
                    >
                      {item.price}
                    </p>
                  </span>
                  <div
                    className={`${item.change > 0 ? "bg-green-card" : item.change === 0 ? "bg-muted-foreground/40" : "bg-red-card"} flex h-10 w-16 items-center justify-center gap-0.5 rounded-[8px]`}
                  >
                    {item.change > 0 ? (
                      <ArrowUp
                        className={`h-4 w-4 shrink-0 stroke-3 ${isFetching ? "text-primary-foreground/60" : "text-primary-foreground"}`}
                      />
                    ) : item.change === 0 ? (
                      <Minus
                        className={`h-4 w-4 shrink-0 stroke-3 ${isFetching ? "text-primary-foreground/60" : "text-primary-foreground"}`}
                      />
                    ) : (
                      <ArrowDown
                        className={`h-4 w-4 shrink-0 stroke-3 ${isFetching ? "text-primary-foreground/60" : "text-primary-foreground"}`}
                      />
                    )}
                    <p
                      className={`text-xs font-semibold ${isFetching ? "text-primary-foreground/60" : "text-primary-foreground"}`}
                    >
                      {item.change !== 0 &&
                        `${item.change.toFixed(2).replace("-", "")}%`}
                    </p>
                  </div>
                </div>
              </CarouselItem>
            ))}
      </CarouselContent>
    </Carousel>
  );
}
