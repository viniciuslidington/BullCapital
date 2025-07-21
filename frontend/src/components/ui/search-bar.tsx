import { Send } from "lucide-react";
import { Button } from "./button";

export function SearchBar() {
  return (
    <div className="flex items-center gap-5">
      {" "}
      <input
        type="text"
        className="bg-background dark:bg-input w-[636px] rounded-[12px] border-1 p-3 shadow-xs"
        placeholder="Pesquisar ações (ex: PETR4, VALE3)"
      />{" "}
      <Button size="lg" className="cursor-pointer p-6">
        <Send />
        PESQUISAR
      </Button>
    </div>
  );
}
