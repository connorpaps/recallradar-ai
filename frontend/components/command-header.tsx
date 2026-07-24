import { Activity, ShieldCheck } from "lucide-react";

export function CommandHeader({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string;
  title: string;
  description?: string;
  children?: React.ReactNode;
}) {
  return (
    <header className="relative overflow-hidden rounded-[2rem] border border-slate-200 bg-[#fbfaf5] p-6 text-ink shadow-soft md:p-8">
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-moss via-amber-400 to-red-500" />
      <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(47,125,89,0.08)_0,transparent_42%,rgba(241,182,80,0.12)_100%)]" />
      <div className="absolute inset-0 opacity-35 [background-image:linear-gradient(rgba(17,26,22,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(17,26,22,0.05)_1px,transparent_1px)] [background-size:44px_44px]" />
      <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-moss/20 bg-white px-3 py-1.5 text-xs font-black uppercase tracking-[0.22em] text-moss shadow-sm">
            <Activity className="h-3.5 w-3.5" />
            {eyebrow}
          </div>
          <h1 className="mt-4 max-w-5xl text-4xl font-black tracking-tight md:text-6xl">{title}</h1>
          {description ? <p className="mt-4 max-w-3xl text-sm font-semibold leading-6 text-slate-600">{description}</p> : null}
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2 text-sm font-black text-ink">
            <ShieldCheck className="h-4 w-4 text-moss" />
            Evidence locked
          </div>
          <p className="mt-2 max-w-xs text-xs leading-5 text-slate-500">Every AI suggestion remains tied to source facts, scoring signals, and human review status.</p>
        </div>
      </div>
      {children ? <div className="relative mt-6">{children}</div> : null}
    </header>
  );
}
