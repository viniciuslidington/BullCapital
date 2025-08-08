import { AlertCircleIcon, Globe, Send } from "lucide-react";
import { Button } from "./button";
import { useSearch } from "@/hooks/queries/usesearch";
import { useState, type FormEventHandler } from "react";
import { Popover, PopoverAnchor, PopoverContent } from "./popover";
import { useNavigate } from "react-router-dom";
import type { SearchResult } from "@/types/search";
import { DotSpinner } from "ldrs/react";
import "ldrs/react/DotSpinner.css";
import { SECTOR_TRANSLATE } from "@/data/sector-data";
import type { Setores } from "@/types/category";

export function SearchBar() {
  const [isSearch, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const { data, isLoading, isError } = useSearch(isSearch);

  const handleSubmit: FormEventHandler = (e) => {
    e.preventDefault();
    const form = e.currentTarget as HTMLFormElement;
    const formData = new FormData(form);
    const inputValue = formData.get("input");
    if (inputValue === "" || inputValue === null) return;
    setSearch(inputValue as string);
    setOpen(true);
  };

  return (
    <Popover modal={false} open={open} onOpenChange={setOpen}>
      <PopoverContent
        className="bg-card/60 !z-6 overflow-hidden rounded-xl p-0 backdrop-blur-sm dark:backdrop-blur-lg"
        sideOffset={16}
      >
        <div className="border-b p-4">
          <p>Resultados para "{isSearch}"</p>
        </div>
        <ul className="flex flex-col gap-1 p-2">
          {isLoading ? (
            <span className="flex w-full justify-center py-5">
              <DotSpinner
                size="40"
                speed="0.9"
                color="var(--loading-spinner) "
              />
            </span>
          ) : isError ? (
            <span className="text-destructive flex w-full items-center justify-center gap-2 py-5">
              <AlertCircleIcon className="h-4 w-4" />
              <p className="text-center text-sm">
                Falha ao carregar resultados
              </p>
            </span>
          ) : (data?.results?.length ?? 0) > 0 ? (
            data?.results.map((result) => (
              <ResultLi key={result.symbol} item={result} />
            ))
          ) : (
            <p className="py-5 text-center text-sm">
              Não foi possível encontrar resultados...
            </p>
          )}
        </ul>
      </PopoverContent>
      <PopoverAnchor>
        <form
          className="relative flex items-center gap-5"
          onSubmit={handleSubmit}
        >
          {" "}
          <input
            name="input"
            type="text"
            className="bg-background dark:bg-input w-[636px] rounded-4xl border-1 px-4 py-3 shadow-xs"
            placeholder="Pesquisar ações (ex: PETR4, VALE3)"
          />{" "}
          <Button
            size="lg"
            className="absolute right-2 cursor-pointer rounded-4xl text-xs"
          >
            <Send />
            PESQUISAR
          </Button>
        </form>
      </PopoverAnchor>
    </Popover>
  );
}

function ResultLi({ item }: { item: SearchResult }) {
  const navigate = useNavigate();
  return (
    <li
      key={item.symbol}
      className="hover:bg-input active:bg-primary flex w-full cursor-pointer items-center gap-4 rounded-[8px] p-2 transition-all duration-200 ease-in-out"
      onClick={() => navigate(item.symbol)}
    >
      {item.logo ? (
        <img src={item.logo || undefined} alt="logo" className="h-8 w-8" />
      ) : (
        <Globe className="text-primary h-8 w-8 shrink-0" />
      )}
      <div className="flex w-full flex-col gap-1">
        <span className="flex items-center justify-between">
          <p className="text-sm font-semibold">
            {item.symbol.replace(".SA", "")}
          </p>

          <p className="text-xs">
            {item.exchange} - {item.type}
          </p>
        </span>
        <span className="flex max-w-[206px] items-center justify-between gap-4 overflow-hidden">
          <p className="text-muted-foreground min-w-0 flex-1 truncate text-xs">
            {item.name}
          </p>
          <p className="text-muted-foreground truncate text-xs">
            {item?.sector ? SECTOR_TRANSLATE[item.sector as Setores] : ""}
          </p>
        </span>
      </div>
    </li>
  );
}
