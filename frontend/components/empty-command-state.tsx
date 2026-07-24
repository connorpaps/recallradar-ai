import { Radar } from "lucide-react";

export function EmptyCommandState({ message }: { message: string }) {
  return (
    <div className="rounded-3xl border border-dashed border-slate-300 bg-white/70 p-8 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-field text-moss">
        <Radar className="h-6 w-6" />
      </div>
      <p className="mt-4 text-sm font-bold text-slate-600">{message}</p>
    </div>
  );
}
