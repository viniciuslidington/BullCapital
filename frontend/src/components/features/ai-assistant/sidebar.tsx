import { createContext, useContext, useState } from "react";
import { SidebarHeader } from "./sidebarheader";
import { SidebarFooter } from "./sidebarfooter";
import { MessagesScroll } from "./messagesScroll";

type ValueContextType = {
  isFixed: boolean;
  toggleFixed: () => void;
  messages: string[];
  addMessageHandler: (message: string) => void;
  clearMessagesHandler: () => void;
};

export const SidebarContext = createContext<ValueContextType | null>(null);

export function Sidebar() {
  const [isFixed, setIsFixed] = useState(false);
  const toggleFixed = () => setIsFixed(!isFixed);

  const [messages, setMessages] = useState<string[]>([]);
  const addMessageHandler = (message: string) =>
    setMessages([...messages, message]);
  const clearMessagesHandler = () => setMessages([]);

  return (
    <SidebarContext.Provider
      value={{
        isFixed,
        toggleFixed,
        messages,
        addMessageHandler,
        clearMessagesHandler,
      }}
    >
      <div
        className={`group bg-background fixed top-20 right-0 flex h-[calc(100vh-80px)] flex-col dark:border-l-1 ${isFixed ? "w-[473px]" : "w-20 hover:w-[473px]"} border-l-2 transition-all duration-400 ease-in-out`}
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
