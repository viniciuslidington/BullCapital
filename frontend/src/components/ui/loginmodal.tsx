import { useAuthByGoogle } from "@/hooks/queries/useauth";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./dialog";
import { Button } from "./button";
import { ChevronDown, User } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./tabs";
import { ScrollArea } from "./scroll-area";
import { LoginForm } from "./loginform";
import { RegisterForm } from "./registerform";

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
                className="w-full cursor-pointer"
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
                <Button
                  variant="outline"
                  className="my-2 w-full cursor-pointer"
                  onClick={() => performGoogleLogin()}
                  disabled={isGooglePending}
                >
                  <GoogleIcon className="mr-2 h-4 w-4" />
                  {isGooglePending ? "A redirecionar..." : "Entrar com Google"}
                </Button>

                <DialogDescription>
                  Ou preencha os campos abaixo para criar sua conta.
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
