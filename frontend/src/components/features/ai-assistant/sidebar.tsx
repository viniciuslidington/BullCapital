import { createContext, useContext, useState } from "react";
import { SidebarHeader } from "./sidebarheader";
import { SidebarFooter } from "./sidebarfooter";
import { MessagesScroll } from "./messagesScroll";
import { useAIChat } from "@/hooks/queries/useaichat";
import type { ChatMessage } from "@/types/ai";
import { ConvoList } from "./convolist";

type ValueContextType = {
  isFixed: boolean;
  toggleFixed: () => void;
  messages: ChatMessage[] | never[];
  isLoading: boolean;
  sendMessage: (content: string) => void;
  clearChat: () => void;
  aiStatus: string | undefined;
  toggleConvoList: () => void;
  setConvoList: React.Dispatch<React.SetStateAction<boolean>>;
  isOpenConvoList: boolean;
  isFetchingHistory: boolean;
};

export const SidebarContext = createContext<ValueContextType | null>(null);

export function Sidebar() {
  const [isFixed, setIsFixed] = useState(false);
  const toggleFixed = () => setIsFixed(!isFixed);
  const [isOpenConvoList, setConvoList] = useState(false);
  const toggleConvoList = () => setConvoList(!isOpenConvoList);

  const {
    chatResponse,
    isLoading,
    sendMessage,
    clearChat,
    aiStatus,
    isFetchingHistory,
  } = useAIChat();

  return (
    <SidebarContext.Provider
      value={{
        isFixed,
        toggleFixed,
        messages: chatResponse?.messages || [],
        isLoading,
        sendMessage,
        clearChat,
        aiStatus,
        toggleConvoList,
        setConvoList,
        isOpenConvoList,
        isFetchingHistory,
      }}
    >
      <div
        className={`group bg-background fixed top-20 right-0 flex h-[calc(100vh-80px)] flex-col ${isFixed ? "w-[473px]" : "w-20 hover:w-[473px]"} z-10 border-l-1 transition-all duration-400 ease-in-out`}
      >
        <SidebarHeader />
        {isOpenConvoList ? <ConvoList /> : <MessagesScroll />}
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
