import { Sparkles, Info } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/common/ErrorState";
import { useSummary } from "@/hooks/useSummary";

interface AiExplanationPanelProps {
  repositoryId: number;
  filePath: string;
}

/** Shows the AI-generated explanation for the selected file. */
export function AiExplanationPanel({
  repositoryId,
  filePath,
}: AiExplanationPanelProps) {
  const { data, isLoading, isError, error, refetch } = useSummary(
    repositoryId,
    filePath,
  );

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Explanation unavailable"
        message={
          error instanceof Error
            ? error.message
            : "The AI explanation could not be generated."
        }
        onRetry={() => refetch()}
      />
    );
  }

  if (!data) return null;

  if (!data.available) {
    return (
      <div className="flex gap-2 rounded-md border border-dashed border-border bg-muted/30 p-3 text-sm text-muted-foreground">
        <Info className="mt-0.5 size-4 shrink-0" />
        <p>{data.summary}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Sparkles className="size-4 text-primary" />
        <span className="text-sm font-medium">AI explanation</span>
        {data.cached && (
          <Badge variant="muted" title="Served from local cache">
            cached
          </Badge>
        )}
        {data.model && <Badge variant="secondary">{data.model}</Badge>}
      </div>
      <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
        {data.summary}
      </p>
    </div>
  );
}
