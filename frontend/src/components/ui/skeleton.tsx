import { cn } from "@/lib/utils";

/** Animated placeholder used while content is loading. */
function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "skeleton-shimmer rounded-md bg-muted/60",
        className,
      )}
      {...props}
    />
  );
}

export { Skeleton };
