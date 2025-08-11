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
      className={`flex flex-1 flex-col items-center gap-5 p-4 pb-24 transition-all duration-200 ease-in-out max-h-[calc(100vh-172px)] overflow-y-auto ${isFixed ? "opacity-100" : "opacity-0 group-hover:opacity-100 group-hover:delay-500"}`}
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
        messages.map((m) => (
          <Message key={m.id} tipo={m.type}>
            {m.content}
          </Message>
        ))
      )}
    </div>
  );
}
