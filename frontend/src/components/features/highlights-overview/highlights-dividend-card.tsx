import { Button } from "@/components/ui/button";
import { formatPrice } from "@/lib/utils";
import type { DividendItem } from "@/types/assets";
import React from "react";
import { useNavigate, type NavigateFunction } from "react-router-dom";

interface HighlightsCardProps {
  title: string;
  items: DividendItem[];
  onSeeMore?: NavigateFunction;
}

export const HighlightsDividendCard: React.FC<HighlightsCardProps> = ({
  title,
  items,
  onSeeMore,
}) => {
  const navigate = useNavigate();
  return (
    <div className="group bg-card text-card-foreground w-[264px] max-w-sm flex-none rounded-xl border-1 shadow-sm transition-all duration-200 ease-in-out hover:shadow-lg">
      <div className="flex flex-row items-center justify-between border-b-1 p-4 pb-5">
        <h3 className="text-muted-foreground group-hover:text-foreground font-medium transition-all duration-200 ease-in">
          {title}
        </h3>
        <Button
          variant="link"
          className="h-auto cursor-pointer p-0 text-sm"
          onClick={onSeeMore}
        >
          Ver Mais
        </Button>
      </div>
      <div>
        <div className="flex flex-col gap-2 p-2">
          {items.map((item) => (
            <div
              key={item.ticker}
              className="hover:bg-input active:bg-primary flex cursor-pointer items-center justify-between rounded-[8px] p-2 transition-all duration-200 ease-in-out"
              onClick={() => navigate(item.ticker)}
            >
              <div>
                <p className="text-md font-semibold">{item.ticker}</p>
                <p className="text-muted-foreground w-[116px] truncate text-sm">
                  {item.nome}
                </p>
              </div>
              <div className="text-right">
                <p className="text-md font-medium">
                  {formatPrice(item.dividendo, item.currency)}
                </p>
                <p className={`text-muted-foreground font-regular text-sm`}>
                  {item.dataPagamento.replaceAll("-", "/")}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
