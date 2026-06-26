import { Activity, Boxes, FileCode2, FunctionSquare, GitBranch } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import { useStats } from "@/hooks/useGraph";
import { formatNumber, languageColor, languageLabel } from "@/utils/format";

/** Compact statistics summary for the active repository. */
export function StatsSummary({ repositoryId }: { repositoryId: number }) {
  const { data, isLoading } = useStats(repositoryId);

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-14" />
        ))}
      </div>
    );
  }
  if (!data) return null;

  const tiles = [
    { icon: <FileCode2 className="size-4" />, label: "Files", value: data.total_files },
    { icon: <GitBranch className="size-4" />, label: "Deps", value: data.total_dependencies },
    { icon: <Boxes className="size-4" />, label: "Classes", value: data.total_classes },
    { icon: <FunctionSquare className="size-4" />, label: "Functions", value: data.total_functions },
  ];

  const maxLines = Math.max(1, ...data.languages.map((l) => l.lines));

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2">
        {tiles.map((t) => (
          <div
            key={t.label}
            className="rounded-md border border-border bg-background/40 p-2.5"
          >
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              {t.icon}
              {t.label}
            </div>
            <div className="mt-1 text-lg font-semibold">
              {formatNumber(t.value)}
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-md border border-border bg-background/40 p-2.5">
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Activity className="size-4" />
          Avg. complexity
        </div>
        <div className="mt-1 text-lg font-semibold">
          {data.average_complexity}
        </div>
      </div>

      {data.languages.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Languages
          </h4>
          <div className="space-y-1.5">
            {data.languages
              .slice()
              .sort((a, b) => b.lines - a.lines)
              .map((lang) => (
                <div key={lang.language} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1.5">
                      <span
                        className="size-2 rounded-full"
                        style={{ backgroundColor: languageColor(lang.language) }}
                      />
                      {languageLabel(lang.language)}
                    </span>
                    <span className="text-muted-foreground">
                      {lang.files} files
                    </span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${(lang.lines / maxLines) * 100}%`,
                        backgroundColor: languageColor(lang.language),
                      }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
