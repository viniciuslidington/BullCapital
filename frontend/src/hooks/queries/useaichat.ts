import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AIService } from "@/services/ai-service";
import type { ChatMessage, ChatRequest, ChatResponse } from "@/types/ai";
import { useCallback, useState } from "react";
import { toast } from "sonner";
import { useSearchParams } from "react-router-dom";

// Para tipar o contexto da mutação e ter um rollback seguro
interface MutationContext {
  previousMessages?: ChatMessage[];
}

export function useAIChat() {
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const [conversationId, setConversationId] = useState<string | undefined>(
    searchParams.get("chat") || undefined,
  );

  const queryKey = ["conversation", conversationId];

  const { data: messages = [], isLoading: isFetchingHistory } = useQuery<
    ChatMessage[]
  >({
    queryKey,
    queryFn: () => AIService.getMessages(conversationId!),
    enabled: !!conversationId,
  });

  const { mutate, isPending: isSendingMessage } = useMutation<
    ChatResponse,
    Error,
    ChatRequest,
    MutationContext // Adicionamos o tipo do contexto aqui
  >({
    mutationFn: ({ question }) =>
      AIService.chat({
        question: question,
        conversation_id: conversationId,
      }),

    onMutate: async ({ question }) => {
      // Cancela qualquer refetch pendente para não sobrescrever nossa atualização otimista.
      await queryClient.cancelQueries({ queryKey });

      // Salva o estado anterior do cache, caso precisemos reverter.
      const previousMessages =
        queryClient.getQueryData<ChatMessage[]>(queryKey);

      // Cria a nova mensagem do usuário com um ID temporário.
      const newUserMessage: ChatMessage = {
        role: "user",
        content: question,
        timestamp: new Date().toISOString(),
      };

      // Atualiza o cache otimisticamente com a nova mensagem.
      queryClient.setQueryData<ChatMessage[]>(queryKey, (old = []) => [
        ...old,
        newUserMessage,
      ]);

      // Retorna o estado anterior no contexto para o 'onError'.
      return { previousMessages };
    },

    onError: (err, variables, context) => {
      console.error("Erro na mutação, revertendo atualização otimista:", err);
      // Se a mutação falhar, usa o contexto do onMutate para reverter ao estado anterior.
      if (context?.previousMessages) {
        queryClient.setQueryData(queryKey, context.previousMessages);
      }
      console.error("Falha ao enviar mensagem:", err);
      toast.error("Falha ao enviar mensagem", {
        description: "Verifique sua conexão e tente novamente.",
      });
    },

    onSettled: (data) => {
      const finalConversationId = data?.conversation_id || conversationId;
      if (data?.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
        setSearchParams({ chat: data.conversation_id });
      }

      queryClient.invalidateQueries({
        queryKey: ["conversation", finalConversationId],
      });
    },
  });

  const sendMessage = (question: string) => {
    if (question.trim()) {
      mutate({ question, conversation_id: conversationId });
    }
  };

  const clearChat = useCallback(() => {
    setConversationId(undefined);
    // Removemos a query do cache para garantir que não haja dados antigos se uma nova conversa começar.
    queryClient.removeQueries({ queryKey: ["conversation"] });
    setSearchParams();
  }, [queryClient, setSearchParams]);

  // O estado de loading geral é uma combinação do carregamento inicial do histórico e do envio de uma nova mensagem.
  const isLoading = isFetchingHistory || isSendingMessage;

  const aiHealth = useQuery({
    queryKey: ["aiHealth"],
    queryFn: AIService.health,
    refetchInterval: 30000, // a cada 30s
    retry: false,
  });

  return {
    messages,
    isLoading,
    conversationId,
    sendMessage,
    clearChat,
    aiHealth,
  };
}
