import { AssetBox } from "./asset-box";

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
  return (
    <div className="flex flex-nowrap justify-between gap-5">
      {response.cards.map((data) => (
        <AssetBox
          key={data.ticker}
          ticker={data.ticker}
          name={data.name}
          value={data.value}
          unit={data.unit}
          changePercent={data.changePercent}
          type={data.type}
        />
      ))}
    </div>
  );
}
