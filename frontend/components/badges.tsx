import { cn } from "@/lib/utils";

const confidenceClasses = {
  high: "border-red-200 bg-red-50 text-red-700",
  medium: "border-amber-200 bg-amber-50 text-amber-800",
  low: "border-slate-200 bg-slate-50 text-slate-700",
};

const statusClasses = {
  needs_review: "border-amber-200 bg-amber-50 text-amber-800",
  confirmed: "border-blue-200 bg-blue-50 text-blue-700",
  dismissed: "border-slate-200 bg-slate-50 text-slate-600",
  resolved: "border-emerald-200 bg-emerald-50 text-emerald-700",
};

export function ConfidenceBadge({ value }: { value?: string | null }) {
  if (!value) return <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-bold text-slate-500">none</span>;
  return (
    <span className={cn("rounded-full border px-2.5 py-1 text-xs font-semibold capitalize", confidenceClasses[value as keyof typeof confidenceClasses])}>
      {value}
    </span>
  );
}

export function StatusBadge({ value }: { value: string }) {
  return (
    <span className={cn("rounded-full border px-2.5 py-1 text-xs font-semibold capitalize", statusClasses[value as keyof typeof statusClasses])}>
      {value.replace("_", " ")}
    </span>
  );
}

export function ClassBadge({ value }: { value?: string | null }) {
  const isCritical = value?.toLowerCase().includes("class i");
  return (
    <span className={cn("rounded-full border px-2.5 py-1 text-xs font-semibold", isCritical ? "border-red-200 bg-red-50 text-red-700" : "border-slate-200 bg-white text-slate-700")}>
      {value ?? "Unclassified"}
    </span>
  );
}

export function SourceBadge({ source }: { source: string }) {
  const isLive = source === "openfda";
  return (
    <span className={cn("rounded-full border px-2.5 py-1 text-xs font-black", isLive ? "border-emerald-200 bg-emerald-50 text-emerald-700" : "border-slate-200 bg-white text-slate-600")}>
      {isLive ? "Live openFDA" : "Demo recall"}
    </span>
  );
}
