import { ScrollArea } from "@/components/ui/scroll-area";
import { Message } from "./message";
import { useSidebar } from "./sidebar";
import Logo from "@/assets/ai-logo.png";
import { useEffect, useRef } from "react";

export function MessagesScroll() {
  const { isFixed, messages } = useSidebar();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [messages.length]);

  return (
    <div
      ref={containerRef}
      className={`flex max-h-[calc(100vh-172px)] flex-1 flex-col gap-5 p-4 pb-[156px] transition-all duration-200 ease-in-out ${isFixed ? "opacity-100" : "opacity-0 group-hover:opacity-100 group-hover:delay-500"}`}
    >
      {messages.length === 0 ? (
        <div className="flex h-[calc(100%-172px)] flex-col items-center justify-center gap-5">
          <img
            src={Logo}
            alt="assistant logo"
            className="aspect-square h-16 w-16"
          />
          <p className="text-muted-foreground text-2xl">Como posso ajudar?</p>
        </div>
      ) : (
        <ScrollArea className="h-full">
          <span className="flex flex-col gap-5 pr-4" ref={containerRef}>
            {messages.map((m) => (
              <Message key={m.timestamp} tipo={m.role}>
                {m.content}
              </Message>
            ))}
          </span>
        </ScrollArea>
      )}
    </div>
  );
}
