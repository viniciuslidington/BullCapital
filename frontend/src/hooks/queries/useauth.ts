import { AuthService } from "@/services/auth-service";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getQueryConfig } from "./queries-config";
import { toast } from "sonner";
import { AxiosError } from "axios";
import type { LoginPayload, RegisterPayload } from "@/types/user";

export function useAuthByGoogle() {
  return useMutation({
    mutationFn: AuthService.loginByGoogle,
    onSuccess: (data) => (window.location.href = data.auth_url),
    onError: (error) => {
      console.error("Falha ao obter URL do Google:", error);
      toast.error("Falha na autenticação", {
        description:
          "Não foi possível iniciar o login com Google. Verifique sua conexão e tente novamente.",
      });
    },
  });
}
export function useUserProfile() {
  return useQuery({
    queryKey: ["user", "profile"],
    queryFn: AuthService.getUser,
    ...getQueryConfig("userProfile"),
  });
}
export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: AuthService.Logout,
    onSuccess: () => {
      // Limpa os dados do usuário do cache para refletir o estado de deslogado
      queryClient.setQueryData(["user", "profile"], null);
    },
    onError: (error) => {
      console.error("Falha ao obter URL do Google:", error);
      toast.error("Falha na autenticação", {
        description:
          "Não foi possível realizar o logout. Verifique sua conexão e tente novamente.",
      });
    },
  });
}

export function useRegisterUser() {
  const queryClient = useQueryClient();

  return useMutation({
    // A função que será chamada para executar a mutação
    mutationFn: (userData: RegisterPayload) => AuthService.Register(userData),

    // O que fazer em caso de sucesso
    onSuccess: (data) => {
      toast.success("Conta criada com sucesso!", {
        description: `Bem-vindo, ${data.nome_completo}!`,
      });
      queryClient.invalidateQueries({ queryKey: ["user", "profile"] });
    },

    // O que fazer em caso de erro
    onError: (error) => {
      // O Axios anexa a resposta do erro a `error.response`
      if (error instanceof AxiosError && error.response) {
        // Exibe a mensagem de erro específica vinda do backend (ex: "Email já existe")
        const errorMessage =
          error.response.data?.detail || "Ocorreu um erro desconhecido.";
        toast.error("Falha no registo", {
          description: errorMessage,
        });
      } else {
        // Erro genérico de rede ou outro
        toast.error("Falha no registo", {
          description:
            "Não foi possível conectar ao servidor. Tente novamente.",
        });
      }
    },
  });
}

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: LoginPayload) => AuthService.Login(credentials),

    // O que fazer em caso de sucesso no login
    onSuccess: (data) => {
      toast.success("Login realizado com sucesso!", {
        description: `Bem-vindo de volta, ${data.nome_completo.split(" ")[0]}!`,
      });

      // ESTE É O PASSO MAIS IMPORTANTE:
      // Após o backend definir o cookie, invalidamos a query do perfil do utilizador.
      // Isto força o React Query a buscar novamente os dados do utilizador,
      // atualizando toda a aplicação para o estado de "logado".
      queryClient.invalidateQueries({ queryKey: ["user", "profile"] });
    },

    // O que fazer em caso de erro no login
    onError: (error) => {
      if (error instanceof AxiosError && error.response) {
        // Exibe a mensagem de erro específica vinda do backend (ex: "Email ou senha incorretos")
        const errorMessage =
          error.response.data?.detail || "Ocorreu um erro desconhecido.";
        toast.error("Falha no login", {
          description: errorMessage,
        });
      } else {
        toast.error("Falha no login", {
          description:
            "Não foi possível conectar ao servidor. Tente novamente.",
        });
      }
    },
  });
}
