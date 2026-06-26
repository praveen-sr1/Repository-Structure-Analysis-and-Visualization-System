import { Boxes, FunctionSquare, GitBranch, Hash, Ruler } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import { useFileMetrics } from "@/hooks/useFileMetrics";
import { complexityBand, formatNumber } from "@/utils/format";

interface MetricsPanelProps {
  repositoryId: number;
  filePath: string;
}

interface MetricRowProps {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
  valueClassName?: string;
}

function MetricRow({ icon, label, value, valueClassName }: MetricRowProps) {
  return (
    <div className="flex items-center justify-between rounded-md border border-border bg-background/40 px-3 py-2">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="text-muted-foreground">{icon}</span>
        {label}
      </div>
      <span className={`text-sm font-semibold ${valueClassName ?? ""}`}>
        {value}
      </span>
    </div>
  );
}

/** Shows numeric metrics for the selected file. */
export function MetricsPanel({ repositoryId, filePath }: MetricsPanelProps) {
  const { data, isLoading } = useFileMetrics(repositoryId, filePath);

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    );
  }
  if (!data) return null;

  const band = complexityBand(data.cyclomatic_complexity);

  return (
    <div className="space-y-2">
      <MetricRow
        icon={<Ruler className="size-4" />}
        label="Lines of code"
        value={formatNumber(data.lines_of_code)}
      />
      <MetricRow
        icon={<GitBranch className="size-4" />}
        label="Imports"
        value={formatNumber(data.num_imports)}
      />
      <MetricRow
        icon={<Boxes className="size-4" />}
        label="Classes"
        value={formatNumber(data.num_classes)}
      />
      <MetricRow
        icon={<FunctionSquare className="size-4" />}
        label="Functions"
        value={formatNumber(data.num_functions)}
      />
      <MetricRow
        icon={<Hash className="size-4" />}
        label="Cyclomatic complexity"
        value={`${data.cyclomatic_complexity} · ${band.label}`}
        valueClassName={band.className}
      />

      <NameList
        title="Classes"
        icon={<Boxes className="size-3.5" />}
        names={data.class_names}
      />
      <NameList
        title="Functions"
        icon={<FunctionSquare className="size-3.5" />}
        names={data.function_names}
      />
    </div>
  );
}

interface NameListProps {
  title: string;
  icon: React.ReactNode;
  names: string[];
}

/** Renders the declared class/function names as compact chips. */
function NameList({ title, icon, names }: NameListProps) {
  if (!names || names.length === 0) return null;
  return (
    <div className="rounded-md border border-border bg-background/40 px-3 py-2">
      <div className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
        {icon}
        {title}
        <span className="text-muted-foreground/70">({names.length})</span>
      </div>
      <div className="flex flex-wrap gap-1">
        {names.map((name) => (
          <span
            key={name}
            className="rounded bg-muted px-1.5 py-0.5 font-mono text-[11px] text-foreground/90"
            title={name}
          >
            {name}
          </span>
        ))}
      </div>
    </div>
  );
}
