import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

type MessageProps = {
  children: string;
  tipo?: "user" | "ai";
};

export function Message({ children, tipo = "user" }: MessageProps) {
  return (
    <div className="flex w-full items-end justify-end gap-2">
      <div className="bg-primary rounded-[12px] rounded-br-none p-3">
        <p className="text-primary-foreground">{children}</p>
      </div>
      <Avatar>
        <AvatarImage src="https://github.com/shadcn.png" />
        <AvatarFallback>CN</AvatarFallback>
      </Avatar>
    </div>
  );
}
