import { Skeleton } from "@/components/ui/skeleton";

export function ListSkeleton({
  key,
  isError = false,
}: {
  key: number;
  isError: boolean;
}) {
  return (
    <div
      key={key}
      className="hover:bg-input active:bg-primary flex h-15 cursor-pointer items-center justify-between rounded-[8px] p-2 transition-all duration-200 ease-in-out"
    >
      <Skeleton animation={!isError} className="h-9 w-9" />
      <div className="flex w-[116px] flex-col items-start gap-2">
        <Skeleton animation={!isError} className="h-3 w-16" />
        <Skeleton animation={!isError} className="h-2 w-25" />
      </div>
      <div className="flex flex-col items-end gap-2">
        <Skeleton animation={!isError} className="h-3 w-15" />
        <Skeleton animation={!isError} className="h-2 w-8" />
      </div>
    </div>
  );
}
