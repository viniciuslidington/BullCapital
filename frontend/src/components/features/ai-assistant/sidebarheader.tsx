import { ChevronsLeft, ChevronsRight, History, SquarePen } from "lucide-react";
import { useSidebar } from "./sidebar";
import { Button } from "@/components/ui/button";
import Logo from "@/assets/ai-logo.png";

export function SidebarHeader() {
  const { isFixed, toggleFixed, clearMessagesHandler } = useSidebar();
  return (
    <div
      className={`border-border flex items-center justify-between p-4 ${isFixed ? "border-b-1" : "group-hover:border-b-1 group-hover:delay-300"}`}
    >
      <span className="flex gap-2">
        <img
          src={Logo}
          alt="assistant logo"
          className="aspect-square h-12 w-12"
        />
        <span
          className={`flex flex-col transition-all duration-200 ease-in-out ${isFixed ? "opacity-100" : "opacity-0 group-hover:opacity-100 group-hover:delay-200"}`}
        >
          <h3 className="text-foreground font-semibold">Assistente IA</h3>
          <p className="text-green-600"> Online</p>
        </span>
      </span>
      <div
        className={`flex transition-all duration-200 ease-in-out ${isFixed ? "opacity-100" : "opacity-0 group-hover:opacity-100 group-hover:delay-200"}`}
      >
        <Button variant="ghost" size="icon" className="size-8 cursor-pointer">
          <History className="text-muted-foreground !h-6 !w-6" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="size-8 cursor-pointer"
          onClick={clearMessagesHandler}
        >
          <SquarePen className="text-muted-foreground !h-5 !w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="size-8 cursor-pointer"
          onClick={toggleFixed}
        >
          {isFixed ? (
            <ChevronsRight className="text-muted-foreground !h-6 !w-6" />
          ) : (
            <ChevronsLeft className="text-muted-foreground !h-6 !w-6" />
          )}
        </Button>
      </div>
    </div>
  );
}
