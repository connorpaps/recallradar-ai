import { CommandHeader } from "@/components/command-header";
import { RecallFilters } from "@/components/recall-filters";
import { RiskWorklistRow } from "@/components/risk-worklist-row";
import { getRecalls } from "@/lib/api";

export default async function RecallsPage({ searchParams }: { searchParams: Promise<{ source?: string; classification?: string; has_matches?: string }> }) {
  const filters = await searchParams;
  const recalls = await getRecalls(filters);
  const exposed = recalls.items.filter((recall) => recall.match_count > 0).length;
  const live = recalls.items.filter((recall) => recall.source === "openfda").length;

  return (
    <div className="flex flex-col gap-6">
      <CommandHeader
        eyebrow="Recall inbox"
        title="Active recall worklist"
        description="A scannable operations queue that combines source notices, class severity, match pressure, and review priority."
      >
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="text-3xl font-black">{recalls.total}</div>
            <div className="text-xs font-bold uppercase tracking-wide text-emerald-50/60">source records</div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="text-3xl font-black">{exposed}</div>
            <div className="text-xs font-bold uppercase tracking-wide text-emerald-50/60">with exposure</div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="text-3xl font-black">{live}</div>
            <div className="text-xs font-bold uppercase tracking-wide text-emerald-50/60">live openFDA</div>
          </div>
        </div>
      </CommandHeader>
      <RecallFilters />
      <div className="panel overflow-hidden">
        <div className="flex items-center justify-between gap-3 border-b border-slate-200 bg-field px-5 py-4">
          <div>
            <h2 className="font-black">Risk worklist</h2>
            <p className="text-sm text-slate-500">Rows are marked by highest confidence exposure signal.</p>
          </div>
          <div className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-black uppercase tracking-wide text-slate-500">
            Live queue
          </div>
        </div>
        {recalls.items.map((recall) => <RiskWorklistRow key={recall.id} recall={recall} />)}
      </div>
    </div>
  );
}
