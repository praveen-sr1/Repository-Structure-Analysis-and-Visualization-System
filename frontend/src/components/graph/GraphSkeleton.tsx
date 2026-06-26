import { Skeleton } from "@/components/ui/skeleton";

/** Loading placeholder shown while the dependency graph is being fetched. */
export function GraphSkeleton() {
  return (
    <div className="relative h-full w-full overflow-hidden p-8">
      <div className="grid grid-cols-3 gap-x-24 gap-y-6">
        {Array.from({ length: 9 }).map((_, i) => (
          <Skeleton
            key={i}
            className="h-16 w-full max-w-[210px]"
            style={{ marginTop: `${(i % 3) * 24}px` }}
          />
        ))}
      </div>
      <div className="absolute bottom-6 right-6">
        <Skeleton className="h-24 w-40" />
      </div>
    </div>
  );
}
