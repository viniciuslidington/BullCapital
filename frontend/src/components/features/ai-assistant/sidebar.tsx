import { createContext, useContext, useState } from "react";
import { SidebarHeader } from "./sidebarheader";
import { SidebarFooter } from "./sidebarfooter";
import { MessagesScroll } from "./messagesScroll";
import { useAIChat } from "@/hooks/useAIChat";
import type { ChatMessage } from "@/types/ai";

type ValueContextType = {
  isFixed: boolean;
  toggleFixed: () => void;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
  analyzeStock: (ticker: string, question?: string) => Promise<void>;
  getFinanceData: (ticker: string) => Promise<void>;
};

export const SidebarContext = createContext<ValueContextType | null>(null);

export function Sidebar() {
  const [isFixed, setIsFixed] = useState(false);
  const toggleFixed = () => setIsFixed(!isFixed);

  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    analyzeStock,
    getFinanceData,
  } = useAIChat();

  return (
    <SidebarContext.Provider
      value={{
        isFixed,
        toggleFixed,
        messages,
        isLoading,
        error,
        sendMessage,
        clearMessages,
        analyzeStock,
        getFinanceData,
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
