import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useSidebar } from "./sidebar";

export function SidebarFooter() {
  const [input, setInput] = useState("");

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { isFixed, messages, addMessageHandler } = useSidebar();

  const suggestions = [
    "Como está o mercado hoje?",
    "Melhores Dividendos",
    "Analisar PETR4",
    "Setores em alta hoje",
    "Quais ações estão em alta?",
  ];

  function handleSubmit() {
    setInput("");
    addMessageHandler(input);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto"; // Reseta a altura para recalcular
      const maxHeight = 24 * 6;
      textarea.style.height = Math.min(textarea.scrollHeight, maxHeight) + "px";
    }
  }, [input]);

  return (
    <div
      className={`absolute bottom-0 flex flex-col gap-3 p-4 transition-all duration-300 ease-in-out ${isFixed ? "opacity-100" : "opacity-0 group-hover:opacity-100 group-hover:delay-200"}`}
      onMouseLeave={() => {
        if (document.activeElement === textareaRef.current) {
          if (textareaRef.current) {
            textareaRef.current.blur();
          }
        }
      }}
    >
      <div
        className={`flex max-w-full flex-wrap gap-2 transition-all duration-300 ease-in-out ${messages.length === 0 && input === "" ? "opacity-100" : "pointer-events-none opacity-0"}`}
      >
        {suggestions.map((s) => (
          <Button
            variant="secondary"
            size="sm"
            className="bg-input cursor-pointer rounded-xl"
            onClick={() => setInput(s)}
            key={s}
          >
            <p className="text-muted-foreground text-xs">{s}</p>
          </Button>
        ))}
      </div>

      <div className="bg-input flex flex-col items-end gap-2 rounded-md p-3">
        <textarea
          placeholder="Digite sua pergunta sobre investimentos"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="placeholder:text-muted-foreground min-w-[415px] resize-none overflow-y-auto text-sm focus:outline-none"
          style={{ lineHeight: "24px", maxHeight: `${6 * 24}px` }}
          rows={1}
          maxLength={1000}
          ref={textareaRef}
          onKeyDown={handleKeyDown}
        />
        <Button
          size="icon"
          onClick={() => handleSubmit()}
          className="cursor-pointer"
        >
          <Send />
        </Button>
      </div>
      <p className="text-muted-foreground w-[440px] text-[12px]">
        Esta é uma ferramenta de apoio e pode apresentar imprecisões. Avalie as
        respostas antes de decidir.
      </p>
    </div>
  );
}
