import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AIService } from "@/services/ai-service";
import {
  type ConversationListResponse,
  type ChatMessage,
  type ChatRequest,
  type ChatResponse,
} from "@/types/ai";
import { useCallback } from "react";
import { toast } from "sonner";
import { useSearchParams } from "react-router-dom";
import { useUserProfile } from "./useauth";

// Tipagem para o contexto da mutação, usado no rollback em caso de erro.
interface MutationContext {
  previousMessages?: ChatMessage[];
}

export function useAIChat() {
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const { data: userData } = useUserProfile();

  // A URL é a única fonte da verdade para o ID da conversa.
  // Não usamos mais useState + useEffect para evitar problemas de sincronia.
  const conversationId = searchParams.get("chat") || null;
  const queryKey = ["conversation", conversationId];

  // Query para buscar as mensagens da conversa ativa.
  const { data: chatResponse, isLoading: isFetchingHistory } =
    useQuery<ChatResponse>({
      queryKey,
      queryFn: () => AIService.getMessages(conversationId!),
      enabled: !!conversationId, // Só executa se houver um conversationId.
    });

  // Mutação para enviar uma nova mensagem.
  const { mutate, isPending: isSendingMessage } = useMutation<
    ChatResponse,
    Error,
    ChatRequest,
    MutationContext
  >({
    mutationFn: (message) => AIService.chat(message),

    onMutate: async ({ content }) => {
      // Cancela queries pendentes para não sobrescrever a atualização otimista.
      await queryClient.cancelQueries({ queryKey });

      const previousChatResponse =
        queryClient.getQueryData<ChatResponse>(queryKey);

      const newUserMessage: ChatMessage = {
        sender: "user",
        content: content,
        timestamp: new Date().toISOString(),
      };

      // Atualiza o cache otimisticamente.
      queryClient.setQueryData<ChatResponse>(queryKey, (oldData) => {
        if (!oldData) {
          return {
            conversation_id: "temp-id",
            messages: [newUserMessage],
            user_id: userData?.id || null,
            temporario: true,
          };
        }
        return {
          ...oldData,
          messages: [...oldData.messages, newUserMessage],
        };
      });

      return { previousMessages: previousChatResponse?.messages };
    },

    onError: (err, variables, context) => {
      // Em caso de erro, reverte a atualização otimista.
      if (context?.previousMessages) {
        queryClient.setQueryData<ChatResponse>(queryKey, (old) => ({
          ...old!,
          messages: context.previousMessages!,
        }));
      }
      toast.error("Falha ao enviar mensagem.");
      console.error("Mutation error:", err);
    },

    onSettled: (data) => {
      const finalConversationId = data?.conversation_id || conversationId;

      // Se a API retornou um novo ID (primeira mensagem), atualiza a URL.
      if (data?.conversation_id && !conversationId) {
        setSearchParams({ chat: data.conversation_id });
      }

      // Invalida a query da conversa para buscar os dados finais do servidor.
      queryClient.invalidateQueries({
        queryKey: ["conversation", finalConversationId],
      });
      // Invalida a lista de conversas para exibir o novo chat na sidebar.
      queryClient.invalidateQueries({ queryKey: ["conversation", "list"] });
    },
  });

  const sendMessage = (content: string) => {
    if (content.trim() && userData?.id) {
      mutate({
        content,
        conversation_id: conversationId,
        sender: "user",
        user_id: userData.id,
      });
    }
  };

  const clearChat = useCallback(() => {
    // Para limpar o chat, apenas removemos o parâmetro da URL.
    setSearchParams({});
    queryClient.removeQueries({ queryKey: ["conversation", conversationId] });
  }, [queryClient, setSearchParams, conversationId]);

  const isLoading = isFetchingHistory || isSendingMessage;

  // Query para buscar a lista de todas as conversas do usuário.
  const { data: conversationList } = useQuery<ConversationListResponse>({
    queryKey: ["conversation", "list"],
    queryFn: () => AIService.getConversations(userData?.id),
    enabled: !!userData?.id,
  });

  // Query para verificar a saúde da API da IA.
  const { data: aiHealth } = useQuery({
    queryKey: ["aiHealth"],
    queryFn: AIService.health,
    refetchInterval: 30000,
    refetchOnWindowFocus: false,
    retry: false,
  });

  return {
    chatResponse,
    isLoading,
    conversationId,
    sendMessage,
    clearChat,
    aiStatus: aiHealth?.status,
    conversationList,
    isFetchingHistory,
  };
}
