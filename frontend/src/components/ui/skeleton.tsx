import { cn } from "@/lib/utils";

function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="skeleton"
      className={cn(
        "animate-pulse rounded-md bg-black/20 dark:bg-white/20",
        className,
      )}
      {...props}
    />
  );
}

export { Skeleton };
