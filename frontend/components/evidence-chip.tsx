import { CheckCircle2, CircleHelp, TriangleAlert } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

const iconMap = {
  strong: CheckCircle2,
  weak: CircleHelp,
  risk: TriangleAlert,
  neutral: CircleHelp,
  positive: CheckCircle2,
  warning: TriangleAlert,
};

export function EvidenceChip({
  label,
  value,
  type = "strong",
  tone,
  icon,
}: {
  label: string;
  value?: string;
  type?: "strong" | "weak" | "risk";
  tone?: "neutral" | "positive" | "warning";
  icon?: ReactNode;
}) {
  const intent = tone ?? type;
  const Icon = iconMap[intent];
  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-black",
        (intent === "strong" || intent === "positive") && "border-emerald-200 bg-emerald-50 text-emerald-800",
        (intent === "weak" || intent === "neutral") && "border-slate-200 bg-white text-slate-600",
        (intent === "risk" || intent === "warning") && "border-amber-200 bg-amber-50 text-amber-800",
      )}
    >
      {icon ?? <Icon className="h-3.5 w-3.5" />}
      <span>{label}</span>
      {value ? <span className="opacity-70">{value}</span> : null}
    </div>
  );
}
