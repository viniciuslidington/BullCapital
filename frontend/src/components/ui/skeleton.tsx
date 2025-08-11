import { cn } from "@/lib/utils";

function Skeleton({
  className,
  animation = true,
  ...props
}: React.ComponentProps<"div"> & { animation?: boolean }) {
  return (
    <div
      data-slot="skeleton"
      className={cn(
        `${animation && "animate-pulse"} rounded-md bg-black/20 dark:bg-white/20`,
        className,
      )}
      {...props}
    />
  );
}

export { Skeleton };
