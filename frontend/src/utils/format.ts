/** Small formatting and presentation helpers. */

/** Map a language name to a representative accent colour (hsl string). */
export function languageColor(language: string): string {
  const colors: Record<string, string> = {
    python: "#3b82f6",
    javascript: "#eab308",
    typescript: "#0ea5e9",
    java: "#ef4444",
    c: "#64748b",
    cpp: "#a855f7",
    unknown: "#6b7280",
  };
  return colors[language] ?? colors.unknown;
}

/** Human-readable language label. */
export function languageLabel(language: string): string {
  const labels: Record<string, string> = {
    python: "Python",
    javascript: "JavaScript",
    typescript: "TypeScript",
    java: "Java",
    c: "C",
    cpp: "C++",
    unknown: "Other",
  };
  return labels[language] ?? language;
}

/** Format an integer with thousands separators. */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat().format(value);
}

/** Map a complexity score to a qualitative band + colour class. */
export function complexityBand(score: number): {
  label: string;
  className: string;
} {
  if (score <= 5) return { label: "Low", className: "text-emerald-500" };
  if (score <= 10) return { label: "Moderate", className: "text-amber-500" };
  if (score <= 20) return { label: "High", className: "text-orange-500" };
  return { label: "Very High", className: "text-red-500" };
}

/** Format an ISO timestamp as a short relative-ish date string. */
export function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}
