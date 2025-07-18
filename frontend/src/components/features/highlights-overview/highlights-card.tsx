import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// 1. Definindo a tipagem para cada item da lista com TypeScript
interface StockItem {
  ticker: string;
  name: string;
  price: number;
  changePercent: number;
}

// 2. Definindo a tipagem para as props do nosso componente
interface HighlightsCardProps {
  title: string;
  items: StockItem[];
  onSeeMore?: () => void; // Função opcional para o botão "Ver Mais"
}

// Helper para formatar o preço como moeda (ex: $187.45)
const formatPrice = (price: number) => {
  return price.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
};

// Helper para formatar a variação, adicionando o sinal de '+'
const formatChange = (change: number) => {
  const sign = change > 0 ? "+" : "";
  return `${sign}${change.toFixed(2)}%`;
};

export const HighlightsCard: React.FC<HighlightsCardProps> = ({
  title,
  items,
  onSeeMore,
}) => {
  return (
    // 3. Usando o componente Card do shadcn como container principal
    <Card className="bg-card text-card-foreground w-full max-w-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="font-medium">{title}</CardTitle>
        <Button
          variant="link"
          className="h-auto p-0 text-sm"
          onClick={onSeeMore}
        >
          Ver Mais
        </Button>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-4">
          {/* 4. Mapeando a lista de itens para renderizar cada linha */}
          {items.map((item) => (
            <div
              key={item.ticker}
              className="hover:bg-input flex cursor-pointer items-center justify-between rounded-[8px] p-2 transition-all duration-100 ease-in-out"
            >
              {/* Lado Esquerdo: Ticker e Nome */}
              <div>
                <p className="text-md font-semibold">{item.ticker}</p>
                <p className="text-muted-foreground text-sm">{item.name}</p>
              </div>
              {/* Lado Direito: Preço e Variação */}
              <div className="text-right">
                <p className="text-md font-medium">{formatPrice(item.price)}</p>
                {/* 5. Aplicando a cor condicionalmente com base no valor */}
                <p
                  className={`text-sm font-medium ${
                    item.changePercent >= 0 ? "text-green-500" : "text-red-500"
                  }`}
                >
                  {formatChange(item.changePercent)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
