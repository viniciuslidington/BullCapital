import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AIService } from "@/services/ai-service";
import type { ChatMessage } from "@/types/ai";
import { useCallback, useState } from "react";
import { toast } from "sonner";

interface ChatResponse {
  conversationId: string;
}

interface SendMessageVars {
  question: string;
  userId?: string;
}

// Para tipar o contexto da mutação e ter um rollback seguro
interface MutationContext {
  previousMessages?: ChatMessage[];
}

export function useAIChat(initialConversationId: string | null = null) {
  const queryClient = useQueryClient();
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversationId,
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
    SendMessageVars,
    MutationContext // Adicionamos o tipo do contexto aqui
  >({
    mutationFn: ({ question, userId }) =>
      AIService.chat(question, conversationId, userId),

    onMutate: async ({ question }) => {
      // Cancela qualquer refetch pendente para não sobrescrever nossa atualização otimista.
      await queryClient.cancelQueries({ queryKey });

      // Salva o estado anterior do cache, caso precisemos reverter.
      const previousMessages =
        queryClient.getQueryData<ChatMessage[]>(queryKey);

      // Cria a nova mensagem do usuário com um ID temporário.
      const newUserMessage: ChatMessage = {
        id: `temp-${Date.now()}`, // ID temporário
        role: "user",
        content: question,
        // Adicione outros campos necessários para a exibição, como timestamp
        createdAt: new Date().toISOString(),
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
      const finalConversationId = data?.conversationId || conversationId;
      if (data?.conversationId && !conversationId) {
        setConversationId(data.conversationId);
      }

      queryClient.invalidateQueries({
        queryKey: ["conversation", finalConversationId],
      });
    },
  });

  const sendMessage = (question: string, userId?: string) => {
    if (question.trim()) {
      mutate({ question, userId });
    }
  };

  const clearChat = useCallback(() => {
    setConversationId(null);
    // Removemos a query do cache para garantir que não haja dados antigos se uma nova conversa começar.
    queryClient.removeQueries({ queryKey: ["conversation"] });
  }, [queryClient]);

  // O estado de loading geral é uma combinação do carregamento inicial do histórico e do envio de uma nova mensagem.
  const isLoading = isFetchingHistory || isSendingMessage;

  return {
    messages,
    isLoading,
    conversationId,
    sendMessage,
    clearChat,
  };
}
