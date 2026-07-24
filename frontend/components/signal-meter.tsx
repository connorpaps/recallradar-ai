import { cn, formatScore } from "@/lib/utils";

export function SignalMeter({
  label,
  name,
  value,
  score,
  detail,
  tone = "ink",
}: {
  label?: string;
  name?: string;
  value?: string | number;
  score?: string | number;
  detail?: string;
  tone?: "ink" | "red" | "amber" | "green";
}) {
  const displayLabel = label ?? name ?? "Signal";
  const displayValue = value ?? score ?? 0;
  const colors = {
    ink: "bg-ink",
    red: "bg-red-500",
    amber: "bg-amber-500",
    green: "bg-emerald-500",
  };

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3 text-xs font-black uppercase tracking-wide text-slate-500">
        <span>{displayLabel}</span>
        <span>{formatScore(displayValue)}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div className={cn("h-full rounded-full", colors[tone])} style={{ width: formatScore(displayValue) }} />
      </div>
      {detail ? <p className="mt-2 text-sm leading-5 text-slate-600">{detail}</p> : null}
    </div>
  );
}
