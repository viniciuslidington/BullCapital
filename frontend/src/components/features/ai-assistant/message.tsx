import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

type MessageProps = {
  children: string;
  tipo?: "user" | "ai";
};

export function Message({ children, tipo = "user" }: MessageProps) {
  const isUser = tipo === "user";
  
  return (
    <div className={`flex w-full items-end gap-2 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <Avatar className="order-1">
          <AvatarImage src="/ai-logo.png" />
          <AvatarFallback>AI</AvatarFallback>
        </Avatar>
      )}
      <div 
        className={`max-w-[80%] rounded-[12px] p-3 ${
          isUser 
            ? "bg-primary text-primary-foreground rounded-br-none order-2" 
            : "bg-muted text-foreground rounded-bl-none order-2"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm">{children}</p>
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
