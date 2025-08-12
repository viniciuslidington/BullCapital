import { createContext, useContext, useState } from "react";
import { SidebarHeader } from "./sidebarheader";
import { SidebarFooter } from "./sidebarfooter";
import { MessagesScroll } from "./messagesScroll";
import { useAIChat } from "@/hooks/queries/useaichat";
import type { ChatMessage } from "@/types/ai";
import type { UseQueryResult } from "@tanstack/react-query";

type ValueContextType = {
  isFixed: boolean;
  toggleFixed: () => void;
  messages: ChatMessage[];
  isLoading: boolean;
  sendMessage: (question: string, userId?: string | undefined) => void;
  clearChat: () => void;
  aiHealth: UseQueryResult<
    {
      status: string;
      service: string;
    },
    Error
  >;
};

export const SidebarContext = createContext<ValueContextType | null>(null);

export function Sidebar() {
  const [isFixed, setIsFixed] = useState(false);
  const toggleFixed = () => setIsFixed(!isFixed);

  const { messages, isLoading, sendMessage, clearChat, aiHealth } = useAIChat();

  return (
    <SidebarContext.Provider
      value={{
        isFixed,
        toggleFixed,
        messages,
        isLoading,
        sendMessage,
        clearChat,
        aiHealth,
      }}
    >
      <div
        className={`group bg-background fixed top-20 right-0 flex h-[calc(100vh-80px)] flex-col ${isFixed ? "w-[473px]" : "w-20 hover:w-[473px]"} z-10 border-l-1 transition-all duration-400 ease-in-out`}
      >
        <SidebarHeader />
        <MessagesScroll />
        <SidebarFooter />
      </div>
    </SidebarContext.Provider>
  );
}

export function useSidebar() {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error(
      "useSidebar deve ser usado dentro de <SidebarContext.Provider>",
    );
  }
  return context;
}
