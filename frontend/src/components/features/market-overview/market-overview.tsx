import { useMarketOverview } from "@/hooks/queries/usemarketoverview";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
} from "@/components/ui/carousel";
import { useNavigate } from "react-router-dom";
import { AlertCircleIcon, ArrowDown, ArrowUp, Minus } from "lucide-react";
import { BoxSkeleton } from "./boxskeleton";

const priceColor = (numero: number, text: boolean) => {
  let base = "";
  if (numero > 0) {
    base = "-green-card";
  } else if (numero === 0 && text) {
    return "text-muted-foreground";
  } else if (numero === 0) {
    base = "-muted";
  } else {
    base = "-red-card";
  }
  if (text) {
    return `text${base}`;
  } else {
    return `bg${base}`;
  }
};

export function MarketOverview() {
  const {
    data: response,
    isLoading,
    isFetching,
    isError,
  } = useMarketOverview("brasil");
  const navigate = useNavigate();

  const badResponse = (isError || response === undefined) && !isLoading;

  return (
    <Carousel
      opts={{ dragFree: true }}
      className={`${badResponse && "pointer-events-none touch-none"}`}
    >
      <CarouselContent className={`select-none ${badResponse && "blur-[3px]"}`}>
        {isLoading
          ? Array.from({ length: 6 }).map((_, idx) => <BoxSkeleton key={idx} />)
          : badResponse
            ? Array.from({ length: 6 }).map((_, idx) => (
                <BoxSkeleton isError={true} key={idx} />
              ))
            : response?.data?.map((item) => (
                <CarouselItem
                  className="border-border bg-card ml-4 flex w-auto shrink-0 grow-0 basis-auto cursor-pointer rounded-[12px] border p-2 shadow-sm transition-all duration-200 ease-in-out hover:shadow-md"
                  onClick={() => navigate(item.symbol)}
                >
                  <div className="flex justify-between gap-3">
                    <div
                      className={`${priceColor(parseFloat(item.change.toFixed(2)), false)} flex h-9 w-9 items-center justify-center gap-0.5 rounded-[8px]`}
                    >
                      {item.change > 0 ? (
                        <ArrowUp
                          className={`h-4 w-4 shrink-0 stroke-3 ${isFetching ? "text-primary-foreground/60" : "text-primary-foreground"}`}
                        />
                      ) : item.change === 0 ? (
                        <Minus
                          className={`h-4 w-4 shrink-0 stroke-3 ${isFetching ? "dark:text-primary-foreground/60 text-muted-foreground/60" : "dark:text-primary-foreground text-muted-foreground"}`}
                        />
                      ) : (
                        <ArrowDown
                          className={`h-4 w-4 shrink-0 stroke-3 ${isFetching ? "text-primary-foreground/60" : "text-primary-foreground"}`}
                        />
                      )}
                    </div>
                    <span className="flex flex-col justify-between">
                      <p className="text-accent-foreground/85 max-w-22 overflow-hidden text-xs font-bold text-ellipsis whitespace-nowrap">
                        {item.name}
                      </p>
                      <p
                        className={`text-xs ${isFetching ? "text-muted-foreground/70" : "text-muted-foreground"}`}
                      >
                        {item.price}
                      </p>
                    </span>
                    <p
                      className={`text-xs font-semibold ${isFetching ? "text-muted-foreground/70" : priceColor(parseFloat(item.change.toFixed(2)), true)}`}
                    >
                      {item.change.toFixed(2).replace("-", "")}%
                    </p>
                  </div>
                </CarouselItem>
              ))}
      </CarouselContent>
      <CarouselNext className="disabled:!border-transparent disabled:!bg-transparent disabled:!text-transparent" />
      {badResponse && (
        <div className="slide-in-from-top fade-in animate-in bg-card absolute top-1/2 right-1/2 m-auto translate-x-1/2 -translate-y-1/2 rounded-lg border p-3 shadow-lg duration-500">
          <p className="text-destructive flex items-center gap-2 text-sm font-medium">
            <AlertCircleIcon className="h-4 w-4" />
            Falha ao carregar itens
          </p>
        </div>
      )}
    </Carousel>
  );
}
