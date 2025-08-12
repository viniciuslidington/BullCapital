import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import aiLogo from "@/assets/ai-logo.png";
import { useUserProfile } from "@/hooks/queries/useauth";
import { User } from "lucide-react";

type MessageProps = {
  children: string;
  tipo?: "user" | "ai";
};

export function Message({ children, tipo = "user" }: MessageProps) {
  const isUser = tipo === "user";
  const { data } = useUserProfile();
  console.log(data);
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
      {isUser && data?.profile_picture ? (
        <Avatar className="order-3">
          <AvatarImage src={data.profile_picture} />
          <AvatarFallback>CN</AvatarFallback>
        </Avatar>
      ) : (
        isUser && (
          <User className="bg-input text-muted-foreground order-3 size-8 rounded-full p-1" />
        )
      )}
    </div>
  );
}
