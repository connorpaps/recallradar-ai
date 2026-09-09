import { FileClock, Radar, ShieldAlert } from "lucide-react";
import { LiveDataBootstrap } from "@/components/live-data-bootstrap";
import { MobileNav } from "@/components/mobile-nav";
import { ModeEvidenceLink, ModeNavLinks } from "@/components/mode-links";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen text-ink">
      <LiveDataBootstrap />
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-80 border-r border-white/10 bg-[#111a16] px-5 py-6 text-white shadow-2xl xl:block">
        <ModeEvidenceLink href="/" className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#f1b650] text-[#111a16] shadow-lg shadow-amber-900/20">
            <Radar className="h-5 w-5" />
          </div>
          <div>
            <div className="text-lg font-black tracking-tight">RecallRadar AI</div>
            <div className="text-xs font-semibold text-emerald-100/70">Food safety operations</div>
          </div>
        </ModeEvidenceLink>
        <div className="mt-6 rounded-3xl border border-white/10 bg-white/[0.06] p-4">
          <div className="flex items-center gap-2 text-xs font-black uppercase tracking-[0.18em] text-amber-200">
            <ShieldAlert className="h-4 w-4" />
            Live risk desk
          </div>
          <p className="mt-3 text-sm leading-6 text-emerald-50/80">
            Monitor recalls, match inventory, and preserve every decision as evidence.
          </p>
        </div>
        <ModeNavLinks />
        <div className="absolute bottom-5 left-5 right-5 rounded-3xl border border-emerald-300/20 bg-emerald-300/10 p-4">
          <div className="flex items-center gap-2 text-sm font-black text-emerald-50">
            <FileClock className="h-4 w-4" />
            Evidence first
          </div>
          <p className="mt-2 text-xs leading-5 text-emerald-50/70">
            AI suggestions stay reviewable with source notices, confidence scoring, signal traces, and audit history.
          </p>
        </div>
      </aside>
      <main className="xl:pl-80">
        <div className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8"><MobileNav />{children}<p className="mt-8 border-t border-slate-200 pt-4 text-xs font-semibold leading-5 text-slate-500">Decision support only. Always follow official recall notices and your organization’s food-safety procedures. Human review is required before action.</p></div>
      </main>
    </div>
  );
}
