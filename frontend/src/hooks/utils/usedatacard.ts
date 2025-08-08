import { useMemo } from "react";
import { useTickerInfo } from "../queries/useticker";

export function useDataCard(symbol: string) {
  const { data } = useTickerInfo(symbol);
  if (data?.type === "INDEX") {
    data["currency"] = "";
  }
  const marketData = useMemo(() => {
    if (!data) {
      return [];
    }
    return [
      {
        title: "Abertura",
        value: data?.priceAndVariation.regularMarketOpen ?? 0,
        unit: "currency",
      },
      {
        title: "Ultimo Fechamento",
        value: data?.priceAndVariation.previousClose ?? 0,
        unit: "currency",
      },
      {
        title: "Variação de hoje(%)",
        value: data?.priceAndVariation.regularMarketChangePercent ?? 0,
        unit: "percent",
      },
      {
        title: "Variações de hoje",
        value: data?.priceAndVariation.regularMarketDayRange,
        unit: "string",
      },
      {
        title: "Variações do ano",
        value: data?.priceAndVariation.fiftyTwoWeekRange,
        unit: "string",
      },
      {
        title: "Volume",
        value: data?.volumeAndLiquidity.volume ?? 0,
        unit: "largeNumber",
      },
      {
        title: "Volume médio 3 meses",
        value: data?.volumeAndLiquidity.averageDailyVolume3Month ?? 0,
        unit: "largeNumber",
      },
    ];
  }, [data]);

  const valuation = useMemo(() => {
    if (!data) return [];
    return [
      {
        title: "Valor de mercado",
        value: data?.valuation.marketCap ?? 0,
        unit: "largeNumber",
      },
      {
        title: "Valor da firma (Enterprise Value)",
        value: data?.valuation.enterpriseValue ?? 0,
        unit: "largeNumber",
      },
      {
        title: "P/L (Trailing PE)",
        value: data?.valuation.trailingPE ?? 0,
        unit: "percent",
      },
      {
        title: "P/L Projetado (Forward PE)",
        value: data?.valuation.forwardPE ?? 0,
        unit: "percent",
      },
      {
        title: "P/VPA (Price to Book)",
        value: data?.valuation.priceToBook ?? 0,
        unit: "percent",
      },
    ];
  }, [data]);

  const rentability = useMemo(() => {
    if (!data) return [];
    return [
      {
        title: "ROE (Retorno sobre Patrimônio)",
        value: data?.rentability.returnOnEquity ?? 0,
        unit: "percent",
      },
      {
        title: "ROA (Retorno sobre Ativos)",
        value: data?.rentability.returnOnAssets ?? 0,
        unit: "percent",
      },
      {
        title: "Margem Líquida",
        value: data?.rentability.profitMargins ?? 0,
        unit: "percent",
      },
      {
        title: "Margem Operacional",
        value: data?.rentability.operatingMargins ?? 0,
        unit: "percent",
      },
      {
        title: "Margem EBITDA",
        value: data?.rentability.ebitdaMargins ?? 0,
        unit: "percent",
      },
    ];
  }, [data]);

  const eficiencyAndCashflow = useMemo(() => {
    if (!data) return [];
    return [
      {
        title: "Lucro Bruto",
        value: data?.eficiencyAndCashflow.grossProfits ?? 0,
        unit: "largeNumber",
      },
      {
        title: "EBITDA",
        value: data?.eficiencyAndCashflow.ebitda ?? 0,
        unit: "largeNumber",
      },
      {
        title: "Fluxo de Caixa Livre",
        value: data?.eficiencyAndCashflow.freeCashflow ?? 0,
        unit: "largeNumber",
      },
      {
        title: "Receita Total",
        value: data?.eficiencyAndCashflow.totalRevenue ?? 0,
        unit: "largeNumber",
      },
    ];
  }, [data]);

  const debtAndSolvency = useMemo(() => {
    if (!data) return [];
    return [
      {
        title: "Dívida Total",
        value: data?.debtAndSolvency.totalDebt ?? 0,
        unit: "largeNumber",
      },
      {
        title: "Dívida / Patrimônio",
        value: data?.debtAndSolvency.debtToEquity ?? 0,
        unit: "percent",
      },
      {
        title: "Quick Ratio",
        value: data?.debtAndSolvency.quickRatio ?? 0,
        unit: "percent",
      },
      {
        title: "Current Ratio",
        value: data?.debtAndSolvency.currentRatio ?? 0,
        unit: "percent",
      },
    ];
  }, [data]);

  const dividends = useMemo(() => {
    if (!data) return [];
    return [
      {
        title: "Dividend Yield",
        value: data?.dividends.dividendYield ?? 0,
        unit: "percent",
      },
      {
        title: "Payout Ratio",
        value: data?.dividends.payoutRatio ?? 0,
        unit: "percent",
      },
      {
        title: "Último Dividendo",
        value: data?.dividends.lastDividendValue ?? 0,
        unit: "currency",
      },
    ];
  }, [data]);

  const shareholdingAndProfit = useMemo(() => {
    if (!data) return [];
    return [
      {
        title: "Lucro por Ação (EPS)",
        value: data?.ShareholdingAndProfit.epsTrailingTwelveMonths ?? 0,
        unit: "currency",
      },
      {
        title: "Lucro por Ação Estimado",
        value: data?.ShareholdingAndProfit.epsForward ?? 0,
        unit: "currency",
      },
      {
        title: "Lucro Líquido",
        value: data?.ShareholdingAndProfit.netIncomeToCommon ?? 0,
        unit: "largeNumber",
      },
    ];
  }, [data]);

  const analystData = useMemo(() => {
    if (!data) {
      return [];
    }

    return [
      {
        title: "Beta",
        value: data.riskAndMarketOpinion.beta ?? null,
        unit: "string", // pode deixar como null ou "" se não for um número formatável
      },
      {
        title: "Recomendação",
        value: data.riskAndMarketOpinion.recommendationKey ?? null,
        unit: "string",
      },
      {
        title: "Nota média",
        value: data.riskAndMarketOpinion.recommendationMean ?? null,
        unit: "string",
      },
      {
        title: "Preço alvo (alto)",
        value: data.riskAndMarketOpinion.targetHighPrice ?? null,
        unit: "currency",
      },
      {
        title: "Preço alvo (baixo)",
        value: data.riskAndMarketOpinion.targetLowPrice ?? null,
        unit: "currency",
      },
      {
        title: "Preço alvo (médio)",
        value: data.riskAndMarketOpinion.targetMeanPrice ?? null,
        unit: "currency",
      },
      {
        title: "Nº de analistas",
        value: data.riskAndMarketOpinion.numberOfAnalystOpinions ?? null,
        unit: "largeNumber",
      },
    ];
  }, [data]);

  return {
    marketData,
    valuation,
    rentability,
    eficiencyAndCashflow,
    debtAndSolvency,
    dividends,
    shareholdingAndProfit,
    analystData,
  };
}
