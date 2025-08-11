import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import aiLogo from "@/assets/ai-logo.png";

type MessageProps = {
  children: string;
  tipo?: "user" | "ai";
};

export function Message({ children, tipo = "user" }: MessageProps) {
  const isUser = tipo === "user";

  return (
    <div
      className={`flex w-full items-end gap-2 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <Avatar className="order-1">
          <AvatarImage src={aiLogo} />
          <AvatarFallback>AI</AvatarFallback>
        </Avatar>
      )}
      <div
        className={`max-w-[80%] rounded-[12px] p-3 ${
          isUser
            ? "bg-primary text-primary-foreground order-2 rounded-br-none"
            : "bg-muted text-foreground order-2 rounded-bl-none"
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{children}</p>
      </div>
      {isUser && (
        <Avatar className="order-3">
          <AvatarImage src="https://github.com/shadcn.png" />
          <AvatarFallback>CN</AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
