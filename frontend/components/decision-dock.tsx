import { AlertTriangle, CheckCircle2, PackageSearch } from "lucide-react";
import { ConfidenceBadge, StatusBadge } from "@/components/badges";
import { ReviewActions } from "@/components/review-actions";
import type { RecallMatch } from "@/types/api";
import { formatExposure, formatScore } from "@/lib/utils";

export function DecisionDock({ match }: { match?: RecallMatch }) {
  if (!match) {
    return (
      <aside className="panel p-5">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-moss" />
          <h2 className="font-black">Decision dock</h2>
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-500">No inventory exposure has been detected for this recall.</p>
      </aside>
    );
  }

  return (
    <aside className="overflow-hidden rounded-[1.75rem] border border-[#24382d] bg-[#111a16] text-white shadow-2xl">
      <div className="border-b border-white/10 p-5">
        <p className="text-xs font-black uppercase tracking-[0.22em] text-amber-200">Decision dock</p>
        <h2 className="mt-2 text-2xl font-black">Top exposure</h2>
      </div>
      <div className="p-5">
        <div className="flex items-start gap-3">
          <div className="rounded-2xl border border-red-200/30 bg-red-500/15 p-3">
            <AlertTriangle className="h-5 w-5 text-red-200" />
          </div>
          <div>
            <h3 className="font-black">{match.inventory_item?.product_name}</h3>
            <p className="mt-1 text-sm leading-6 text-emerald-50/70">{match.explanation}</p>
          </div>
        </div>
        <div className="mt-5 grid grid-cols-2 gap-3">
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="text-xs font-bold text-emerald-50/60">Score</div>
            <div className="mt-1 text-3xl font-black">{formatScore(match.score)}</div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="text-xs font-bold text-emerald-50/60">Exposure</div>
            <div className="mt-1 text-3xl font-black">{formatExposure(match.exposure_score)}</div>
          </div>
        </div>
        <div className="mt-3 rounded-2xl border border-white/10 bg-white/10 p-4">
          <div className="text-xs font-bold text-emerald-50/60">Location</div>
          <div className="mt-2 flex items-center gap-2 text-sm font-black">
            <PackageSearch className="h-4 w-4 text-amber-200" />
            {match.inventory_item?.location ?? "Unassigned"}
          </div>
          <p className="mt-2 text-xs font-semibold leading-5 text-emerald-50/70">{match.exposure_factors.summary}</p>
        </div>
        <div className="mt-5 flex flex-wrap gap-2">
          <ConfidenceBadge value={match.confidence} />
          <StatusBadge value={match.status} />
        </div>
        <div className="mt-5 rounded-2xl bg-white p-3 text-ink">
          <ReviewActions matchId={match.id} />
        </div>
      </div>
    </aside>
  );
}
