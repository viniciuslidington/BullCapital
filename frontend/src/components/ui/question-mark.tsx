import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { CircleQuestionMark } from "lucide-react";

type IndexType =
  | "price"
  | "priceChangePercent"
  | "roe"
  | "dy"
  | "yearHigh"
  | "marketCap"
  | "peRatio"
  | "netMargin"
  | "pFfo"
  | "pVp";

const textByIndex = {
  price: `Preço atual da ação, ETF ou outro ativo no mercado. Representa o valor pelo qual o ativo está sendo negociado no momento da consulta.`,
  priceChangePercent: `Representa a variação percentual do preço do ativo em um determinado período (normalmente 1 dia). Indica se o ativo valorizou ou desvalorizou em relação ao fechamento anterior.`,
  roe: `ROE (Return on Equity) mede a rentabilidade de uma empresa em relação ao patrimônio líquido dos acionistas. Indica quanto lucro líquido é gerado para cada unidade de capital próprio investido, mostrando a eficiência da gestão. \n\nA fórmula é: Lucro Líquido ÷ Patrimônio Líquido, com resultado expresso em percentual.`,
  dy: `Dividend Yield indica o retorno em dividendos que o investidor recebe em relação ao preço atual da ação. É uma medida da rentabilidade dos dividendos pagos pela empresa. \n\nA fórmula é: (Dividendos Anuais ÷ Preço da Ação) × 100%.`,
  yearHigh: `Preço máximo atingido pelo ativo nos últimos 52 semanas (1 ano). É um indicador importante para avaliar o potencial de valorização e resistência do preço.`,
  marketCap: `Valor total de mercado da empresa calculado pela multiplicação do preço da ação pelo número total de ações em circulação. \n\nA fórmula é: Preço da Ação × Número de Ações.`,
  peRatio: `O Índice Preço/Lucro (P/L) mede quanto os investidores estão dispostos a pagar por cada unidade de lucro da empresa. \n\nA fórmula é: Preço da Ação ÷ Lucro por Ação (LPA).`,
  netMargin: `Margem Líquida indica a porcentagem do lucro líquido obtido sobre a receita total da empresa, mostrando a eficiência operacional. \n\nA fórmula é: (Lucro Líquido ÷ Receita Total) × 100%.`,
  pFfo: `Preço sobre Funds From Operations (P/FFO) é um indicador usado para avaliar fundos imobiliários, relacionando o preço do ativo com o fluxo de caixa operacional. \n\nA fórmula é: Preço da Cota ÷ FFO por Cota.`,
  pVp: `Este índice compara o preço da cota do fundo imobiliário com seu valor patrimonial, indicando se está sendo negociado acima ou abaixo do valor contábil. \n\nA fórmula é: Preço da Cota ÷ Valor Patrimonial por Cota.`,
};

export function QuestionMark({ index }: { index: IndexType }) {
  return (
    <Tooltip>
      <TooltipTrigger>
        <CircleQuestionMark className="text-primary mt-1 h-4 w-4 cursor-pointer" />
      </TooltipTrigger>
      <TooltipContent side="right" className="max-w-full p-0 text-wrap">
        <p className="max-w-[400px] p-3 text-justify font-medium hyphens-auto whitespace-pre-line lg:max-w-[464px]">
          {textByIndex[index]}
        </p>
      </TooltipContent>
    </Tooltip>
  );
}
