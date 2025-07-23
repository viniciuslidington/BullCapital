import { useNavigate } from "react-router-dom";

type AssetProps = {
  key: string;
  ticker: string;
  name: string;
  value: number;
  unit: string;
  type: string;
  changePercent: number;
};

export function AssetBox({
  ticker,
  name,
  value,
  unit,
  changePercent,
  type,
}: AssetProps) {
  const navigate = useNavigate();
  return (
    <div
      className="bg-card border-border flex h-20 cursor-pointer flex-col justify-center gap-2 rounded-[12px] border-1 px-3 shadow-sm transition-all duration-200 ease-in-out hover:shadow-md"
      onClick={() => navigate(ticker)}
    >
      <div className="flex items-end justify-between gap-5">
        <p className="text-sm font-medium whitespace-nowrap">{name}</p>
        <div
          className={`${changePercent > 0 ? "bg-green-card" : "bg-red-card"} rounded-[8px] px-1 py-[2px]`}
        >
          <p className="text-primary-foreground font-medium">
            {changePercent}%
          </p>
        </div>
      </div>
      <p className="text-accent-foreground text-xs font-medium">{`${type === "currency" ? unit : ""}${value}${type !== "currency" ? unit : ""}`}</p>
    </div>
  );
}
