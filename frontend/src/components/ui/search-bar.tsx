import { Send } from "lucide-react";
import { Button } from "./button";

export function SearchBar() {
  return (
    <div className="relative flex items-center gap-5">
      {" "}
      <input
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
    </div>
  );
}
