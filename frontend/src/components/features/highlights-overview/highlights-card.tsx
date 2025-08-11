import { Button } from "@/components/ui/button";
import { formatChange, formatPrice } from "@/lib/utils";
import type { CategoriaResult } from "@/types/category";
import React, { type MouseEventHandler } from "react";
import { useNavigate, type NavigateFunction } from "react-router-dom";
import { ListSkeleton } from "./listskeleton";
import { CarouselItem } from "@/components/ui/carousel";
import { Globe } from "lucide-react";

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

export const HighlightsCard: React.FC<HighlightsCardProps> = ({
  title,
  items,
  onSeeMore,
  fetchState,
}) => {
  const navigate = useNavigate();

  return (
    <CarouselItem className="group bg-card/60 text-card-foreground z-9 ml-5 w-[264px] max-w-sm flex-none rounded-xl border-1 pl-0 shadow-sm transition-all duration-200 ease-in-out hover:shadow-lg">
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
          {fetchState.isLoading || fetchState.badResponse || items.length === 0
            ? Array.from({ length: 5 }).map((_, idx) => (
                <ListSkeleton isError={fetchState.badResponse} key={idx} />
              ))
            : items.map((item) => (
                <div
                  key={item.symbol}
                  className="hover:bg-input active:bg-primary flex cursor-pointer items-center justify-between rounded-[8px] p-2 transition-all duration-200 ease-in-out"
                  onClick={() => navigate(item.symbol)}
                >
                  {item.logo ? (
                    <img
                      src={item.logo || undefined}
                      alt="logo"
                      className="h-8 w-8"
                    />
                  ) : (
                    <Globe className="text-primary h-8 w-8" />
                  )}
                  <div>
                    <p className="text-md font-semibold">
                      {item.symbol.replace(".SA", "")}
                    </p>
                    <p className="text-muted-foreground w-[116px] truncate text-xs">
                      {item.name}
                    </p>
                  </div>
                  <div className="text-right">
                    <p
                      className={`text-md font-medium ${fetchState.isFetching && "opacity-70"}`}
                    >
                      {formatPrice(item.price, item.currency)}
                    </p>
                    <p
                      className={`text-sm font-medium ${
                        item.change >= 0 ? "text-green-500" : "text-red-500"
                      } ${fetchState.isFetching && "opacity-70"}`}
                    >
                      {formatChange(item.change)}
                    </p>
                  </div>
                </div>
              ))}
        </div>
      </div>
    </CarouselItem>
  );
};
