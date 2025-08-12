import { useAIChat } from "@/hooks/queries/useaichat";
import { useSearchParams } from "react-router-dom";
import { useSidebar } from "./sidebar";
import { ScrollArea } from "@radix-ui/react-scroll-area";

export function ConvoList() {
  const { conversationList } = useAIChat();
  const [, setSearchParams] = useSearchParams();
  const { setConvoList, isFixed } = useSidebar();
  return (
    <div
      className={`flex h-full max-h-[calc(100vh-172px)] w-full flex-1 flex-col gap-5 p-4 pb-[156px] transition-all duration-150 ease-in-out ${isFixed ? "opacity-100" : "opacity-0 group-hover:opacity-100 group-hover:delay-300"}`}
    >
      <p className="text-foreground/80 text-lg font-medium">
        Histórico de Conversas
      </p>
      <ScrollArea className="h-full pr-4">
        <ul className="flex flex-col gap-2">
          {conversationList?.conversations.map((convo) => (
            <li
              key={convo.id}
              className="bg-primary flex cursor-pointer items-center justify-between rounded-md px-2 py-3 transition-all duration-100 ease-in-out hover:bg-purple-500"
              onClick={() => {
                setConvoList(false);
                setSearchParams({ chat: convo.id });
              }}
            >
              <p className="max-w-[264px] truncate text-sm font-medium">
                {convo.title}
              </p>
              <p className="text-sm">
                {new Date(convo.last_message).toLocaleString("pt-BR", {
                  day: "2-digit",
                  month: "2-digit",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                  hour12: false,
                })}
              </p>
            </li>
          ))}
        </ul>
      </ScrollArea>
    </div>
  );
}
