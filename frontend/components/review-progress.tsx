import { SignalMeter } from "@/components/signal-meter";

export function ReviewProgress({ byStatus }: { byStatus: Record<string, number> }) {
  const total = Object.values(byStatus).reduce((sum, value) => sum + value, 0) || 1;
  const resolved = (byStatus.resolved ?? 0) + (byStatus.dismissed ?? 0) + (byStatus.confirmed ?? 0);

  return (
    <div className="panel p-5">
      <h2 className="text-xl font-black">Review progress</h2>
      <p className="mt-1 text-sm text-slate-500">Human decisions across the current exposure set.</p>
      <div className="mt-5">
        <SignalMeter label="decision coverage" value={resolved / total} tone="green" />
      </div>
      <div className="mt-5 grid gap-2">
        {["needs_review", "confirmed", "dismissed", "resolved"].map((key) => (
          <div key={key} className="flex items-center justify-between rounded-2xl bg-field px-3 py-2 text-sm">
            <span className="font-bold capitalize text-slate-600">{key.replace("_", " ")}</span>
            <span className="font-black">{byStatus[key] ?? 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
