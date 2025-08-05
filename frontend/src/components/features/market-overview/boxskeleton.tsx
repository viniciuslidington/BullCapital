import { CarouselItem } from "@/components/ui/carousel";
import { Skeleton } from "@/components/ui/skeleton";

export function BoxSkeleton({
  key,
  isError = false,
}: {
  key: number;
  isError?: boolean;
}) {
  return (
    <CarouselItem
      key={key}
      className="border-border bg-card ml-4 flex w-auto shrink-0 grow-0 basis-auto cursor-pointer rounded-[12px] border p-2 shadow-sm transition-all duration-200 ease-in-out hover:shadow-md"
    >
      <div className="flex justify-between gap-3">
        <Skeleton animation={!isError} className="h-9 w-9"></Skeleton>
        <span className="flex flex-col justify-between py-0.5">
          <span className="flex gap-1">
            <Skeleton animation={!isError} className="h-3 w-20"></Skeleton>
            <Skeleton animation={!isError} className="h-3 w-5"></Skeleton>
          </span>

          <Skeleton animation={!isError} className="h-3 w-10"></Skeleton>
        </span>
      </div>
    </CarouselItem>
  );
}
