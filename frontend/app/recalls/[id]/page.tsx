import { Building2, CalendarDays, FileText, MapPin, PackageCheck } from "lucide-react";
import { AuditTimeline } from "@/components/audit-timeline";
import { ClassBadge, ConfidenceBadge, SourceBadge, StatusBadge } from "@/components/badges";
import { CommandHeader } from "@/components/command-header";
import { DecisionDock } from "@/components/decision-dock";
import { EmptyCommandState } from "@/components/empty-command-state";
import { EvidenceChip } from "@/components/evidence-chip";
import { ReviewActions } from "@/components/review-actions";
import { SignalMeter } from "@/components/signal-meter";
import { getRecall, getRecallMatches } from "@/lib/api";
import { formatDate, formatExposure, formatScore } from "@/lib/utils";

export default async function RecallDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [recall, matches] = await Promise.all([getRecall(id), getRecallMatches(id)]);
  const topMatch = matches.items[0];
  const hasSemanticSignal = matches.items.some((match) => match.signals.some((signal) => signal.name === "semantic_similarity"));

  return (
    <div className="flex flex-col gap-6">
      <CommandHeader
        eyebrow="Recall case file"
        title={recall.product_description}
        description={recall.summary ?? "Review the source recall, matching evidence, inventory exposure, and final human decision in one auditable workspace."}
      >
        <div className="flex flex-wrap gap-2">
          <ClassBadge value={recall.classification} />
          <SourceBadge source={recall.source} />
          <span className="rounded-full border border-white/10 bg-white/10 px-2.5 py-1 text-xs font-semibold">{formatDate(recall.recall_initiation_date)}</span>
          <span className="rounded-full border border-white/10 bg-white/10 px-2.5 py-1 text-xs font-semibold">{matches.items.length} matched items</span>
        </div>
      </CommandHeader>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_22rem]">
        <main className="flex flex-col gap-5">
          <section className="panel p-5">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-moss" />
              <h2 className="text-xl font-black">Source intelligence</h2>
            </div>
            <div className="mt-5 grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-slate-100 bg-field p-4">
                <div className="text-xs font-black uppercase tracking-wide text-slate-500">Firm</div>
                <div className="mt-2 flex items-start gap-2 text-sm font-bold">
                  <Building2 className="mt-0.5 h-4 w-4 shrink-0 text-moss" />
                  {recall.recalling_firm ?? "Unknown"}
                </div>
              </div>
              <div className="rounded-2xl border border-slate-100 bg-field p-4">
                <div className="text-xs font-black uppercase tracking-wide text-slate-500">Report date</div>
                <div className="mt-2 flex items-center gap-2 text-sm font-bold">
                  <CalendarDays className="h-4 w-4 text-moss" />
                  {formatDate(recall.report_date ?? recall.recall_initiation_date)}
                </div>
              </div>
              <div className="rounded-2xl border border-slate-100 bg-field p-4">
                <div className="text-xs font-black uppercase tracking-wide text-slate-500">Source ID</div>
                <div className="mt-2 break-all text-sm font-bold">{recall.source_recall_id}</div>
              </div>
            </div>
            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <div>
                <h3 className="text-sm font-black uppercase tracking-wide text-slate-500">Reason for recall</h3>
                <p className="mt-2 text-sm leading-6 text-slate-700">{recall.reason_for_recall ?? "No reason provided."}</p>
              </div>
              <div>
                <h3 className="text-sm font-black uppercase tracking-wide text-slate-500">Distribution pattern</h3>
                <p className="mt-2 text-sm leading-6 text-slate-700">{recall.distribution_pattern ?? "No distribution details provided."}</p>
              </div>
            </div>
          </section>

          <section className="panel p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-moss">AI support</p>
                <h2 className="mt-1 text-xl font-black">Summary and semantic evidence</h2>
              </div>
              <span className="rounded-full border border-slate-200 bg-field px-3 py-1 text-xs font-black text-slate-600">
                {hasSemanticSignal ? "AI semantic signal active" : "AI disabled: deterministic matching active"}
              </span>
            </div>
            <p className="mt-4 text-sm font-semibold leading-6 text-slate-600">
              {recall.summary ?? "Deterministic summary unavailable. Review the source reason, distribution pattern, and match evidence below."}
            </p>
            <p className="mt-3 text-xs font-bold text-slate-400">
              Semantic similarity is supporting evidence only; review decisions remain tied to source facts and human status.
            </p>
          </section>

          <section className="panel overflow-hidden">
            <div className="border-b border-slate-200 bg-field px-5 py-4">
              <h2 className="text-xl font-black">Matched inventory evidence</h2>
              <p className="text-sm text-slate-500">Comparison cards expose every scoring signal behind the recommendation.</p>
            </div>
            <div className="grid gap-4 p-5">
              {matches.items.length ? matches.items.map((match) => (
                <article key={match.id} className="overflow-hidden rounded-[1.5rem] border border-slate-200 bg-white shadow-sm">
                  <div className="grid gap-4 border-b border-slate-100 bg-gradient-to-r from-white to-field p-5 lg:grid-cols-[1fr_10rem_10rem]">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-lg font-black">{match.inventory_item?.product_name}</h3>
                        <ConfidenceBadge value={match.confidence} />
                        <StatusBadge value={match.status} />
                      </div>
                      <p className="mt-2 text-sm leading-6 text-slate-600">{match.explanation}</p>
                    </div>
                    <div className="rounded-2xl border border-slate-100 bg-white p-4">
                      <div className="text-xs font-black uppercase tracking-wide text-slate-400">match score</div>
                      <div className="mt-1 text-3xl font-black">{formatScore(match.score)}</div>
                      <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
                        <div className="h-full rounded-full bg-red-500" style={{ width: formatScore(match.score) }} />
                      </div>
                    </div>
                    <div className="rounded-2xl border border-red-100 bg-red-50 p-4">
                      <div className="text-xs font-black uppercase tracking-wide text-red-400">exposure</div>
                      <div className="mt-1 text-3xl font-black text-red-700">{formatExposure(match.exposure_score)}</div>
                      <div className="mt-1 text-xs font-black uppercase text-red-500">{match.exposure_level}</div>
                    </div>
                  </div>
                  <div className="grid gap-5 p-5 lg:grid-cols-[15rem_1fr]">
                    <div className="flex flex-col gap-2">
                      <EvidenceChip icon={<MapPin className="h-3.5 w-3.5" />} label={match.inventory_item?.location ?? "Unassigned"} tone="neutral" />
                      {match.inventory_item?.location_type ? <EvidenceChip label={match.inventory_item.location_type.replaceAll("_", " ")} tone="warning" /> : null}
                      <EvidenceChip icon={<PackageCheck className="h-3.5 w-3.5" />} label={`${match.inventory_item?.quantity ?? "-"} ${match.inventory_item?.unit ?? "units"}`} tone="neutral" />
                      {match.inventory_item?.upc ? <EvidenceChip label={`UPC ${match.inventory_item.upc}`} tone="positive" /> : null}
                      {match.inventory_item?.lot_code ? <EvidenceChip label={`Lot ${match.inventory_item.lot_code}`} tone="warning" /> : null}
                      <div className="mt-2">
                        <ReviewActions matchId={match.id} />
                      </div>
                    </div>
                    <div className="grid gap-3 md:grid-cols-2">
                      <div className="rounded-2xl border border-red-100 bg-red-50 p-4 md:col-span-2">
                        <div className="text-xs font-black uppercase tracking-wide text-red-500">Exposure factors</div>
                        <p className="mt-2 text-sm font-semibold leading-6 text-red-900">{match.exposure_factors.summary}</p>
                      </div>
                      {match.signals.map((signal) => (
                        <SignalMeter key={signal.name} name={signal.name === "semantic_similarity" ? "AI semantic signal" : signal.name.replaceAll("_", " ")} score={signal.score} detail={signal.name === "semantic_similarity" ? `${signal.detail} Supporting evidence only.` : signal.detail} />
                      ))}
                    </div>
                  </div>
                </article>
              )) : (
                <EmptyCommandState message="No matches yet. Run matching from the dashboard to generate evidence." />
              )}
            </div>
          </section>
        </main>

        <aside className="flex flex-col gap-5 xl:sticky xl:top-5 xl:self-start">
          <DecisionDock match={topMatch} />
          <AuditTimeline events={recall.audit_events} />
        </aside>
      </div>
    </div>
  );
}
