import Link from "next/link";
import { Building2, CalendarDays } from "lucide-react";
import { ClassBadge, ConfidenceBadge, SourceBadge } from "@/components/badges";
import type { Recall } from "@/types/api";
import { cn, formatDate } from "@/lib/utils";

const railByConfidence: Record<string, string> = {
  high: "bg-red-500",
  medium: "bg-amber-500",
  low: "bg-moss",
};

export function RiskWorklistRow({ recall }: { recall: Recall }) {
  const rail = railByConfidence[recall.highest_confidence ?? ""] ?? "bg-slate-300";

  return (
    <Link
      href={`/recalls/${recall.id}`}
      className="group grid gap-4 border-b border-slate-100 bg-white px-4 py-4 transition hover:bg-field md:grid-cols-[1fr_9rem_8rem_7rem]"
    >
      <div className="flex gap-4">
        <div className={cn("mt-1 h-16 w-1.5 shrink-0 rounded-full shadow-sm", rail)} />
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-black leading-snug text-ink group-hover:underline">{recall.product_description}</h3>
            <ClassBadge value={recall.classification} />
            <SourceBadge source={recall.source} />
          </div>
          <div className="mt-2 flex flex-wrap gap-2 text-xs font-bold text-slate-500">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-field px-2.5 py-1">
              <Building2 className="h-3.5 w-3.5" />
              {recall.brand_name ?? recall.recalling_firm ?? "Unknown firm"}
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-field px-2.5 py-1">
              <CalendarDays className="h-3.5 w-3.5" />
              {formatDate(recall.recall_initiation_date)}
            </span>
          </div>
        </div>
      </div>
      <div className="self-center">
        <div className="text-xs font-black uppercase tracking-wide text-slate-400">Signal</div>
        <div className="mt-2"><ConfidenceBadge value={recall.highest_confidence} /></div>
      </div>
      <div className="self-center">
        <div className="text-xs font-black uppercase tracking-wide text-slate-400">Matches</div>
        <div className="mt-1 text-2xl font-black text-ink">{recall.match_count}</div>
      </div>
      <div className="self-center text-sm font-black text-moss">Open</div>
    </Link>
  );
}
