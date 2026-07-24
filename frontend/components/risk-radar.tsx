import type { RecallMatch } from "@/types/api";
import { cn, formatExposure } from "@/lib/utils";

const sectors: Record<string, number> = {
  hospital: -75,
  campus_dining: -20,
  grocery_floor: 35,
  food_bank: 95,
  storage: 155,
};

const radiusByLevel = { critical: 52, high: 82, medium: 112, low: 136 };
const colorByLevel = {
  critical: "bg-red-600 text-white border-red-200",
  high: "bg-red-500 text-white border-red-200",
  medium: "bg-amber-400 text-ink border-amber-200",
  low: "bg-moss text-white border-moss/20",
};

function nodeStyle(match: RecallMatch) {
  const type = match.inventory_item?.location_type ?? "storage";
  const angle = ((sectors[type] ?? 155) * Math.PI) / 180;
  const radius = radiusByLevel[match.exposure_level] ?? 136;
  return {
    left: `calc(50% + ${Math.cos(angle) * radius}px)`,
    top: `calc(50% + ${Math.sin(angle) * radius}px)`,
  };
}

export function RiskRadar({ matches, totalReviews }: { matches: RecallMatch[]; totalReviews: number }) {
  const exposure = matches.length ? Math.max(...matches.map((match) => Number(match.exposure_score))) : 0;

  return (
    <div className="relative min-h-[30rem] overflow-hidden rounded-[2rem] border border-slate-200 bg-[#fbfaf5] p-6 text-ink shadow-soft">
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-moss via-amber-400 to-red-500" />
      <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(47,125,89,0.08),transparent_44%,rgba(241,182,80,0.13))]" />
      <div className="absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full border border-moss/15 bg-white/35" />
      <div className="absolute left-1/2 top-1/2 h-56 w-56 -translate-x-1/2 -translate-y-1/2 rounded-full border border-moss/20" />
      <div className="absolute left-1/2 top-1/2 h-36 w-36 -translate-x-1/2 -translate-y-1/2 rounded-full border border-amber-400/45" />
      <div className="absolute left-1/2 top-1/2 h-px w-[82%] -translate-x-1/2 bg-slate-300/80" />
      <div className="absolute left-1/2 top-1/2 h-[82%] w-px -translate-y-1/2 bg-slate-300/80" />
      <div className="absolute left-1/2 top-1/2 h-40 w-1 origin-bottom -translate-x-1/2 -translate-y-full rotate-45 rounded-full bg-gradient-to-t from-amber-400/70 to-transparent" />
      <div className="relative z-10 flex items-start justify-between">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.24em] text-moss">Risk radar</p>
          <h2 className="mt-2 text-2xl font-black">Exposure field</h2>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-right shadow-sm">
          <div className="text-4xl font-black">{formatExposure(exposure)}</div>
          <div className="text-xs font-bold text-slate-500">max exposure</div>
        </div>
      </div>
      {matches.slice(0, 6).map((match, index) => (
        <div
          key={match.id}
          className="absolute z-10 -translate-x-1/2 -translate-y-1/2"
          style={nodeStyle(match)}
          title={`${match.inventory_item?.product_name}: exposure ${formatExposure(match.exposure_score)}`}
        >
          <div className="relative">
            <div className="absolute inset-0 rounded-full bg-red-400 opacity-35 blur-md" />
            <div
              className={cn(
                "relative flex items-center justify-center rounded-full border text-xs font-black shadow-lg",
                colorByLevel[match.exposure_level],
              )}
              style={{
                height: `${Math.min(56, Math.max(36, 28 + Number(match.inventory_item?.quantity ?? 0) / 3))}px`,
                width: `${Math.min(56, Math.max(36, 28 + Number(match.inventory_item?.quantity ?? 0) / 3))}px`,
              }}
            >
              {formatExposure(match.exposure_score)}
            </div>
          </div>
        </div>
      ))}
      <div className="absolute right-6 top-24 z-10 rounded-2xl border border-slate-200 bg-white/90 p-3 text-xs font-bold text-slate-600 shadow-sm">
        <div>Ring: exposure level</div>
        <div>Sector: location type</div>
        <div>Size: quantity</div>
      </div>
      <div className="absolute bottom-6 left-6 right-6 z-10 grid gap-3 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
          <div className="text-lg font-black">{matches.length}</div>
          <div className="text-xs font-bold text-slate-500">priority nodes</div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
          <div className="text-lg font-black">{totalReviews}</div>
          <div className="text-xs font-bold text-slate-500">open reviews</div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
          <div className="text-lg font-black">Live</div>
          <div className="text-xs font-bold text-slate-500">live FDA</div>
        </div>
      </div>
    </div>
  );
}
