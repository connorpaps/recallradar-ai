import { Clock3 } from "lucide-react";
import type { AuditEvent } from "@/types/api";
import { formatDate } from "@/lib/utils";

export function AuditTimeline({ events }: { events: AuditEvent[] }) {
  return (
    <section className="panel overflow-hidden">
      <div className="border-b border-slate-200 bg-field px-5 py-4">
        <div className="flex items-center gap-2">
          <Clock3 className="h-4 w-4 text-moss" />
          <h2 className="font-black">Operational case log</h2>
        </div>
      </div>
      <div className="flex flex-col gap-3 p-5">
        {events.length ? events.map((event) => (
          <div key={event.id} className="relative rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
            <div className="absolute left-0 top-5 h-7 w-1 rounded-r-full bg-moss" />
            <div className="pl-2 text-sm font-black capitalize text-ink">{event.event_type.replaceAll(".", " ")}</div>
            <div className="mt-1 pl-2 text-xs font-semibold text-slate-500">{formatDate(event.created_at)}</div>
            <div className="mt-2 pl-2 text-xs text-slate-500">{event.actor_label ?? event.actor_type}</div>
          </div>
        )) : (
          <div className="rounded-2xl border border-dashed border-slate-200 bg-white p-5 text-sm font-semibold text-slate-500">
            No case activity recorded yet.
          </div>
        )}
      </div>
    </section>
  );
}
