import { AlertTriangle, ClipboardCheck, PackageSearch, Radar } from "lucide-react";
import { SignalMeter } from "@/components/signal-meter";

export function ExposureScoreCard({
  activeRecalls,
  inventoryItems,
  needsReview,
  highConfidence,
  exposureCounts,
}: {
  activeRecalls: number;
  inventoryItems: number;
  needsReview: number;
  highConfidence: number;
  exposureCounts?: Record<string, number>;
}) {
  const exposure = Math.min(1, (needsReview + highConfidence * 2) / Math.max(inventoryItems, 1));
  const urgent = (exposureCounts?.critical ?? 0) + (exposureCounts?.high ?? 0);
  const metrics = [
    { label: "Active recalls", value: activeRecalls, icon: Radar },
    { label: "Inventory items", value: inventoryItems, icon: PackageSearch },
    { label: "Needs review", value: needsReview, icon: ClipboardCheck },
    { label: "High confidence", value: highConfidence, icon: AlertTriangle },
  ];

  return (
    <div className="panel p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.2em] text-moss">Exposure score</p>
          <div className="mt-3 text-5xl font-black">{Math.round(exposure * 100)}</div>
        </div>
        <span className="rounded-full bg-red-50 px-3 py-1 text-xs font-black text-red-700">{urgent} urgent</span>
      </div>
      <div className="mt-5">
        <SignalMeter label="Portfolio demo pressure" value={exposure} tone={highConfidence ? "red" : "amber"} />
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {metrics.map((metric) => (
          <div key={metric.label} className="rounded-2xl border border-slate-100 bg-field p-3">
            <metric.icon className="h-4 w-4 text-moss" />
            <div className="mt-2 text-2xl font-black">{metric.value}</div>
            <div className="text-xs font-bold text-slate-500">{metric.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
