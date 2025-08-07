import { Globe, Send } from "lucide-react";
import { Button } from "./button";
import { useSearch } from "@/hooks/queries/usesearch";
import { useState, type FormEventHandler } from "react";
import { Popover, PopoverAnchor, PopoverContent } from "./popover";
import { formatChange, formatPrice } from "@/lib/utils";
import { useNavigate } from "react-router-dom";
import type { SearchResult } from "@/types/search";

export function SearchBar() {
  const [isSearch, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const { data } = useSearch(isSearch);

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
        className="bg-card/60 !z-6 rounded-xl p-0 backdrop-blur-lg"
        sideOffset={16}
      >
        <div className="border-b p-4">
          <p>Resultados para "{isSearch}"</p>
        </div>
        <ul>
          {data?.results.map((result) => (
            <ResultLi item={result} />
          ))}
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
    <div
      key={item.symbol}
      className="hover:bg-input active:bg-primary flex cursor-pointer items-center justify-between rounded-[8px] p-2 transition-all duration-200 ease-in-out"
      onClick={() => navigate(item.symbol)}
    >
      {item.logo ? (
        <img src={item.logo || undefined} alt="logo" className="h-8 w-8" />
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
        <p className={`text-md font-medium`}></p>
      </div>
    </div>
  );
}
