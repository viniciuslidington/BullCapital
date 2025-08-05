import { Button } from "@/components/ui/button";
import type { CategoriaResult } from "@/types/category";
import React, { type MouseEventHandler } from "react";
import { useNavigate, type NavigateFunction } from "react-router-dom";
import { ListSkeleton } from "./listskeleton";
import { CarouselItem } from "@/components/ui/carousel";

interface HighlightsCardProps {
  title: string;
  items: CategoriaResult[];
  onSeeMore?: NavigateFunction;
  fetchState: {
    isLoading: boolean;
    isFetching: boolean;
    badResponse: boolean;
  };
}

export const HighlightsDividendCard: React.FC<HighlightsCardProps> = ({
  title,
  items,
  onSeeMore,
  fetchState,
}) => {
  const navigate = useNavigate();
  return (
    <CarouselItem className="group bg-card text-card-foreground ml-5 w-[264px] max-w-sm flex-none rounded-xl border-1 pl-0 shadow-sm transition-all duration-200 ease-in-out hover:shadow-lg">
      <div className="flex flex-row items-center justify-between border-b-1 p-4 pb-5">
        <h3 className="text-muted-foreground group-hover:text-foreground font-medium transition-all duration-200 ease-in">
          {title}
        </h3>
        <Button
          variant="link"
          className="h-auto cursor-pointer p-0 text-sm"
          onClick={onSeeMore as MouseEventHandler<HTMLButtonElement>}
        >
          Ver Mais
        </Button>
      </div>
      <div>
        <div className="flex flex-col gap-2 p-2">
          {fetchState.isLoading || fetchState.badResponse
            ? Array.from({ length: 5 }).map((_, idx) => (
                <ListSkeleton isError={fetchState.badResponse} key={idx} />
              ))
            : items.map((item) => (
                <div
                  key={item.symbol}
                  className="hover:bg-input active:bg-primary flex min-h-15 cursor-pointer items-center justify-between rounded-[8px] p-2 transition-all duration-200 ease-in-out"
                  onClick={() => navigate(item.symbol)}
                >
                  <img
                    src={item.logo || undefined}
                    alt="logo"
                    className="h-8 w-8"
                  />
                  <div>
                    <p className="text-md font-semibold">{item.symbol}</p>
                    <p className="text-muted-foreground w-[116px] truncate text-xs">
                      {item.name}
                    </p>
                  </div>
                  <div className="flex h-10 w-15 items-start justify-end text-right">
                    <p
                      className={`text-md font-medium ${fetchState.isFetching && "opacity-70"}`}
                    >
                      {item.dividend_yield}
                    </p>
                    {/* <p className={`text-muted-foreground font-regular text-sm`}>
                      {item.dataPagamento.replaceAll("-", "/")}
                    </p> */}
                  </div>
                </div>
              ))}
        </div>
      </div>
    </CarouselItem>
  );
};
