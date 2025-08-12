import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "./button";
import { ChevronDown, Moon, Sun } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useTheme } from "@/contexts/theme-provider";
import { Logo } from "./logo";
import { useLogout, useUserProfile } from "@/hooks/queries/useauth";

import { LoginModal } from "./loginmodal";
import { ModeToggle } from "./mode-toggle";

export function Header() {
  const { setTheme } = useTheme();
  const { data } = useUserProfile();
  const { mutate: logout, isPending: isLoggingOut } = useLogout();
  return (
    <header className="bg-background border-border fixed top-0 z-10 flex h-20 w-full items-center justify-between border-b-1 px-5 shadow-sm">
      <Logo />
      <div className="flex h-full items-center gap-4">
        {data ? (
          <DropdownMenu modal={false}>
            <DropdownMenuTrigger>
              <Button
                variant="ghost"
                size="default"
                className="cursor-pointer py-6"
              >
                <Avatar className="h-9 w-9">
                  <AvatarImage src={data.profile_picture ?? ""} />
                  <AvatarFallback>{data.nome_completo ?? ""}</AvatarFallback>
                </Avatar>
                <p className="trucate max-w-[124px]">
                  {data.nome_completo ?? ""}
                </p>
                <ChevronDown className="ml-auto" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[164px]">
              <DropdownMenuLabel className="flex items-center gap-2 py-2">
                <Avatar className="h-6 w-6">
                  <AvatarImage src={data.profile_picture ?? ""} />
                  <AvatarFallback>{data.nome_completo ?? ""}</AvatarFallback>
                </Avatar>
                {data.nome_completo ?? ""}
              </DropdownMenuLabel>
              <DropdownMenuSeparator />

              <DropdownMenuSub>
                <DropdownMenuSubTrigger icon={false} className="py-2">
                  <span className="flex items-center gap-[6px]">
                    Tema{" "}
                    <Sun className="h-4 w-4 scale-100 rotate-0 transition-all dark:hidden dark:scale-0 dark:-rotate-90" />
                    <Moon className="hidden h-4 w-4 scale-0 rotate-90 transition-all dark:flex dark:scale-100 dark:rotate-0" />
                  </span>
                </DropdownMenuSubTrigger>
                <DropdownMenuPortal>
                  <DropdownMenuSubContent>
                    <DropdownMenuItem onClick={() => setTheme("light")}>
                      Light
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setTheme("dark")}>
                      Dark
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setTheme("system")}>
                      System
                    </DropdownMenuItem>
                  </DropdownMenuSubContent>
                </DropdownMenuPortal>
              </DropdownMenuSub>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="py-2">Conta</DropdownMenuItem>
              <DropdownMenuItem className="py-2">Pagamento</DropdownMenuItem>
              <DropdownMenuItem
                variant="destructive"
                className={`cursor-pointer py-2 ${isLoggingOut && "pointer-events-none opacity-70"}`}
                onClick={() => logout()}
              >
                Sair
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <span className="flex items-center gap-2">
            <LoginModal />
            <ModeToggle />
          </span>
        )}
      </div>
    </header>
  );
}
