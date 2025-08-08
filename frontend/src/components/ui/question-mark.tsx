import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { categoriaData } from "@/data/categoria-data";
import { indexesData } from "@/data/indexes-data";
import type { CategoriasType, IndexesType } from "@/types/assets";
import { CircleQuestionMark } from "lucide-react";
import type { ReactNode } from "react";

type QuestionMarkProps = {
  dataIndex: string;
  dataType: "indexes" | "categoryDescription" | "categoryTitle";
  children?: ReactNode;
  icon?: boolean;
  side?: "right" | "top" | "bottom" | "left" | undefined;
  delay?: number;
};

export function QuestionMark({
  dataIndex,
  dataType,
  children,
  icon = true,
  side = "right",
  delay = 0,
}: QuestionMarkProps) {
  return (
    <Tooltip delayDuration={delay}>
      <TooltipTrigger>
        {icon && (
          <CircleQuestionMark
            onMouseDown={(e) => e.preventDefault()}
            className="text-primary mt-1 h-4 w-4"
          />
        )}
        {children}
      </TooltipTrigger>
      <TooltipContent side={side} className={`max-w-full text-wrap`}>
        <p
          className={`max-w-[400px] text-left font-medium whitespace-pre-line lg:max-w-[464px] ${dataType === "categoryTitle" ? "" : "p-2"}`}
        >
          {dataType === "indexes"
            ? indexesData[dataIndex as IndexesType].description
            : dataType === "categoryDescription"
              ? categoriaData[dataIndex as CategoriasType].discription
              : dataType === "categoryTitle"
                ? categoriaData[dataIndex as CategoriasType].title
                : null}
        </p>
      </TooltipContent>
    </Tooltip>
  );
}
