import { ChevronsLeft, ChevronsRight, History, SquarePen } from "lucide-react";
import { useSidebar } from "./sidebar";
import { Button } from "@/components/ui/button";
import Logo from "@/assets/ai-logo.png";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useUserProfile } from "@/hooks/queries/useauth";

export function SidebarHeader() {
  const {
    isFixed,
    toggleFixed,
    clearChat,
    aiHealth: { data: healthData },
  } = useSidebar();
  const { data: userData } = useUserProfile();
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
          {healthData?.status === "healty" ? (
            <p className="text-green-600"> Online</p>
          ) : (
            <p className="text-destructive"> Offline</p>
          )}
        </span>
      </span>
      <div
        className={`flex transition-all duration-200 ease-in-out ${isFixed ? "opacity-100" : "opacity-0 group-hover:opacity-100 group-hover:delay-200"}`}
      >
        {userData && (
          <Tooltip disableHoverableContent>
            <TooltipTrigger>
              <Button
                variant="ghost"
                size="icon"
                className="size-8 cursor-pointer"
              >
                <History className="text-muted-foreground !h-6 !w-6" />
              </Button>
            </TooltipTrigger>
            <TooltipContent sideOffset={5} portal={false}>
              <p>Histórico de conversas</p>
            </TooltipContent>
          </Tooltip>
        )}

        <Tooltip disableHoverableContent>
          <TooltipTrigger>
            <Button
              variant="ghost"
              size="icon"
              className="size-8 cursor-pointer"
              onClick={clearChat}
            >
              <SquarePen className="text-muted-foreground !h-5 !w-5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent sideOffset={5} portal={false}>
            <p>Nova conversa</p>
          </TooltipContent>
        </Tooltip>
        <Tooltip disableHoverableContent>
          <TooltipTrigger>
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
          </TooltipTrigger>
          <TooltipContent sideOffset={5} portal={false}>
            <p>{isFixed ? "Desfixar chat" : "Fixar chat"}</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </div>
  );
}
