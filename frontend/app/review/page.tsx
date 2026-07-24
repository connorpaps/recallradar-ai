import Link from "next/link";
import { AlertTriangle, ArrowUpRight, CheckCircle2 } from "lucide-react";
import { ConfidenceBadge, StatusBadge } from "@/components/badges";
import { CommandHeader } from "@/components/command-header";
import { EmptyCommandState } from "@/components/empty-command-state";
import { ReviewActions } from "@/components/review-actions";
import { SignalMeter } from "@/components/signal-meter";
import { getMatches } from "@/lib/api";
import { formatExposure, formatScore } from "@/lib/utils";
import type { RecallMatch } from "@/types/api";

const laneMeta = {
  high: { title: "Critical triage", color: "border-red-200 bg-red-50 text-red-700" },
  medium: { title: "Operational review", color: "border-amber-200 bg-amber-50 text-amber-800" },
  low: { title: "Watchlist", color: "border-slate-200 bg-slate-50 text-slate-700" },
};

function MatchCard({ match }: { match: RecallMatch }) {
  return (
    <article className="rounded-[1.5rem] border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <Link href={`/recalls/${match.recall_id}`} className="font-black leading-snug hover:underline">
            {match.inventory_item?.product_name}
          </Link>
          <p className="mt-2 text-sm leading-6 text-slate-600">{match.explanation}</p>
        </div>
        <Link href={`/recalls/${match.recall_id}`} className="rounded-full border border-slate-200 bg-field p-2 text-slate-600 transition hover:bg-white" aria-label="Open recall">
          <ArrowUpRight className="h-4 w-4" />
        </Link>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <ConfidenceBadge value={match.confidence} />
        <StatusBadge value={match.status} />
        <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold">Score {formatScore(match.score)}</span>
        <span className="rounded-full border border-red-100 bg-red-50 px-2.5 py-1 text-xs font-black text-red-700">Exposure {formatExposure(match.exposure_score)}</span>
      </div>
      <div className="mt-4">
        <SignalMeter label="Operational exposure" value={Number(match.exposure_score) / 100} tone={match.exposure_level === "critical" || match.exposure_level === "high" ? "red" : match.exposure_level === "medium" ? "amber" : "ink"} />
        <p className="mt-2 text-xs font-semibold leading-5 text-slate-500">{match.exposure_factors.summary}</p>
      </div>
      <div className="mt-4">
        <ReviewActions matchId={match.id} />
      </div>
    </article>
  );
}

export default async function ReviewPage() {
  const matches = await getMatches("needs_review");
  const lanes = (["high", "medium", "low"] as const).map((confidence) => ({
    confidence,
    items: matches.items.filter((match) => match.confidence === confidence),
  }));

  return (
    <div className="flex flex-col gap-6">
      <CommandHeader
        eyebrow="Human review"
        title="Evidence triage queue"
        description="A lane-based decision desk for confirming, dismissing, or resolving possible recall exposure before it becomes an operational incident."
      >
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="flex items-center gap-2 text-amber-200"><AlertTriangle className="h-4 w-4" /><span className="text-xs font-black uppercase tracking-wide">needs review</span></div>
            <div className="mt-2 text-3xl font-black">{matches.total}</div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="text-xs font-black uppercase tracking-wide text-emerald-50/60">high confidence</div>
            <div className="mt-2 text-3xl font-black">{lanes[0].items.length}</div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="flex items-center gap-2 text-emerald-100"><CheckCircle2 className="h-4 w-4" /><span className="text-xs font-black uppercase tracking-wide">human gated</span></div>
            <div className="mt-2 text-sm font-semibold text-emerald-50/70">No automated closure without review.</div>
          </div>
        </div>
      </CommandHeader>

      {matches.items.length ? (
        <section className="grid gap-5 xl:grid-cols-3">
          {lanes.map((lane) => (
            <div key={lane.confidence} className="panel overflow-hidden">
              <div className="flex items-center justify-between border-b border-slate-200 bg-field p-4">
                <div>
                  <h2 className="font-black">{laneMeta[lane.confidence].title}</h2>
                  <p className="text-sm text-slate-500">{lane.items.length} cases</p>
                </div>
                <span className={`rounded-full border px-2.5 py-1 text-xs font-black capitalize ${laneMeta[lane.confidence].color}`}>
                  {lane.confidence}
                </span>
              </div>
              <div className="flex flex-col gap-4 p-4">
                {lane.items.length ? lane.items.map((match) => <MatchCard key={match.id} match={match} />) : (
                  <div className="rounded-2xl border border-dashed border-slate-200 bg-white p-5 text-sm font-semibold text-slate-500">No cases in this lane.</div>
                )}
              </div>
            </div>
          ))}
        </section>
      ) : (
        <EmptyCommandState message="No items need review. Import live FDA recalls and run matching to populate this queue." />
      )}
    </div>
  );
}
