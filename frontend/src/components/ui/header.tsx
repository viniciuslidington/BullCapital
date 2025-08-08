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
import { ChevronDown, Moon, Sun, User } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useTheme } from "@/contexts/theme-provider";
import { Logo } from "./logo";
import {
  useAuthByGoogle,
  useLogout,
  useUserProfile,
} from "@/hooks/queries/useauth";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { DialogHeader } from "./dialog";
import { Input } from "./input";
import { Label } from "./label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./tabs";
import { ScrollArea } from "./scroll-area";
import { LoginForm } from "./loginform";
import { RegisterForm } from "./registerform";

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
                  <AvatarImage src="https://github.com/shadcn.png" />
                  <AvatarFallback>LM</AvatarFallback>
                </Avatar>
                Luiz Miguel
                <ChevronDown className="ml-auto" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[164px]">
              <DropdownMenuLabel className="flex items-center gap-2 py-2">
                <Avatar className="h-6 w-6">
                  <AvatarImage src="https://github.com/shadcn.png" />
                  <AvatarFallback>LM</AvatarFallback>
                </Avatar>
                Luiz Miguel
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
          <LoginModal />
        )}
      </div>
    </header>
  );
}

function GoogleIcon({ className }: { className: string }) {
  return (
    <img
      className={className}
      src="https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url=https://www.google.com"
    />
  );
}

export function LoginModal() {
  // Hook para o login com Google (fluxo de redirecionamento)
  const { mutate: performGoogleLogin, isPending: isGooglePending } =
    useAuthByGoogle();

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="default" className="p-6">
          <User className="bg-input text-muted-foreground size-9 shrink-0 rounded-full p-1" />
          Entrar
          <ChevronDown className="ml-auto" />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[504px] p-10 sm:max-w-[425px]">
        <Tabs defaultValue="login" className="flex w-full flex-col gap-5">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Entrar</TabsTrigger>
            <TabsTrigger value="register">Criar Conta</TabsTrigger>
          </TabsList>

          <ScrollArea className="-mr-4 max-h-[380px] overflow-hidden pr-4">
            <TabsContent value="login">
              <DialogHeader>
                <DialogTitle>Acesse sua conta</DialogTitle>
                <DialogDescription>
                  Use um provedor ou seu email para continuar.
                </DialogDescription>
              </DialogHeader>
              <div className="pt-4">
                <LoginForm />{" "}
              </div>
              <div className="relative flex h-16 items-center justify-center">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <span className="bg-background text-muted-foreground z-10 px-2 text-xs uppercase">
                  Ou entrar com
                </span>
              </div>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => performGoogleLogin()}
                disabled={isGooglePending}
              >
                <GoogleIcon className="mr-2 h-4 w-4" />
                {isGooglePending ? "A redirecionar..." : "Entrar com Google"}
              </Button>
            </TabsContent>

            <TabsContent value="register">
              <DialogHeader>
                <DialogTitle>Crie sua conta</DialogTitle>
                <DialogDescription>
                  Preencha os campos abaixo para criar sua conta.
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <RegisterForm />{" "}
              </div>
            </TabsContent>
          </ScrollArea>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
