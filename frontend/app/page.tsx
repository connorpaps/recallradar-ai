import { ArrowUpRight, MapPin, PackageCheck } from "lucide-react";
import { ActionBar } from "@/components/action-bar";
import { ConfidenceBadge, StatusBadge } from "@/components/badges";
import { CommandHeader } from "@/components/command-header";
import { EmptyCommandState } from "@/components/empty-command-state";
import { ExposureScoreCard } from "@/components/exposure-score-card";
import { ReviewProgress } from "@/components/review-progress";
import { RiskRadar } from "@/components/risk-radar";
import { getDashboard, getDemoCompanies, getImportStatus } from "@/lib/api";
import { formatDate, formatExposure } from "@/lib/utils";
import Link from "next/link";

export default async function DashboardPage() {
  const [dashboard, companies, importStatus] = await Promise.all([getDashboard(), getDemoCompanies(), getImportStatus()]);

  return (
    <div>
      <ActionBar companies={companies} selectedCompanyId={dashboard.current_inventory_company?.id ?? null} importStatus={importStatus} />
      <CommandHeader
        eyebrow="Recall operations"
        title="Food safety intelligence, on command."
        description={`A decision desk for imported recall notices, local stock exposure, confidence-scored evidence, and human resolution.${dashboard.current_inventory_company?.name ? ` Current inventory: ${dashboard.current_inventory_company.name}.` : ""}`}
      />
      <section className="mt-6 grid gap-3 md:grid-cols-3">
        <div className="rounded-3xl border border-white/70 bg-white/85 p-4 shadow-soft">
          <div className="text-xs font-black uppercase tracking-wide text-slate-400">Current inventory</div>
          <div className="mt-1 text-lg font-black">{dashboard.current_inventory_company?.name ?? "Uploaded or unassigned inventory"}</div>
          <div className="mt-1 text-xs font-semibold text-slate-500">{dashboard.current_inventory_company?.item_count ?? dashboard.inventory_items} stock rows</div>
        </div>
        <div className="rounded-3xl border border-emerald-100 bg-emerald-50 p-4 shadow-soft">
          <div className="text-xs font-black uppercase tracking-wide text-emerald-700">Live openFDA recalls</div>
          <div className="mt-1 text-3xl font-black text-emerald-900">{dashboard.recall_source_counts.openfda ?? 0}</div>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-soft">
          <div className="text-xs font-black uppercase tracking-wide text-slate-400">Live refresh</div>
          <div className="mt-1 text-lg font-black">Auto-loaded</div>
          <div className="mt-1 text-xs font-semibold text-slate-500">Latest FDA data loads on page refresh</div>
        </div>
      </section>
      <section className="mt-6 grid gap-5 xl:grid-cols-[minmax(0,1fr)_23rem]">
        <RiskRadar matches={dashboard.high_risk_matches} totalReviews={dashboard.matches_needing_review} />
        <div className="flex flex-col gap-5">
          <ExposureScoreCard
            activeRecalls={dashboard.active_recalls}
            inventoryItems={dashboard.inventory_items}
            needsReview={dashboard.matches_needing_review}
            highConfidence={dashboard.high_confidence_matches}
            exposureCounts={dashboard.matches_by_exposure}
          />
          <ReviewProgress byStatus={dashboard.matches_by_status} />
        </div>
      </section>
      <section className="mt-5 grid gap-5 xl:grid-cols-[1fr_23rem]">
        <div className="panel overflow-hidden">
          <div className="flex items-center justify-between gap-3 border-b border-slate-200 p-5">
            <div>
              <h2 className="text-xl font-black">Priority action queue</h2>
              <p className="text-sm text-slate-500">High-confidence inventory exposure sorted for immediate review.</p>
            </div>
            <Link href="/review" className="btn-secondary text-xs">
              Open queue <ArrowUpRight className="h-3.5 w-3.5" />
            </Link>
          </div>
          <div className="divide-y divide-slate-100">
            {dashboard.high_risk_matches.length ? dashboard.high_risk_matches.map((match) => (
              <Link key={match.id} href={`/recalls/${match.recall_id}`} className="group grid gap-4 p-5 transition hover:bg-field lg:grid-cols-[1fr_12rem]">
                <div className="flex gap-4">
                  <div className="mt-1 h-14 w-1.5 rounded-full bg-red-500 shadow-lg shadow-red-500/20" />
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-black">{match.inventory_item?.product_name}</h3>
                      <ConfidenceBadge value={match.confidence} />
                      <StatusBadge value={match.status} />
                    </div>
                    <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{match.recall?.product_description}</p>
                    <div className="mt-3 flex flex-wrap gap-2 text-xs font-bold text-slate-500">
                      <span className="inline-flex items-center gap-1 rounded-full bg-white px-2.5 py-1"><MapPin className="h-3 w-3" />{match.inventory_item?.location ?? "Unassigned"}</span>
                      <span className="inline-flex items-center gap-1 rounded-full bg-white px-2.5 py-1"><PackageCheck className="h-3 w-3" />{match.inventory_item?.quantity ?? "-"} units</span>
                    </div>
                  </div>
                </div>
                <div className="self-center">
                  <div className="text-right text-xs font-black uppercase tracking-wide text-slate-500">exposure</div>
                  <div className="mt-2 h-3 overflow-hidden rounded-full bg-slate-100">
                    <div className="h-full rounded-full bg-red-500" style={{ width: `${Math.min(100, Number(match.exposure_score))}%` }} />
                  </div>
                  <div className="mt-2 text-right text-2xl font-black">{formatExposure(match.exposure_score)}</div>
                  <div className="text-right text-xs font-bold uppercase text-slate-400">{match.exposure_level}</div>
                </div>
              </Link>
            )) : (
              <EmptyCommandState message="Import live FDA recalls and run matching to populate the priority queue." />
            )}
          </div>
        </div>
        <div className="panel p-5">
          <h2 className="text-xl font-black">Case log</h2>
          <p className="mt-1 text-sm text-slate-500">Latest system evidence events.</p>
          <div className="mt-5 flex flex-col gap-3">
            {dashboard.recent_activity.length ? dashboard.recent_activity.map((event) => (
              <div key={event.id} className="relative rounded-2xl border border-slate-100 bg-field p-4">
                <div className="absolute left-0 top-5 h-6 w-1 rounded-r-full bg-moss" />
                <div className="pl-2 text-sm font-black capitalize">{event.event_type.replace(".", " ")}</div>
                <div className="mt-1 pl-2 text-xs font-semibold text-slate-500">{formatDate(event.created_at)}</div>
              </div>
            )) : <EmptyCommandState message="No activity yet." />}
          </div>
        </div>
      </section>
    </div>
  );
}
