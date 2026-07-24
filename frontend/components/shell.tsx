import { Boxes, ClipboardCheck, Database, FileClock, LayoutDashboard, Radar, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { LiveDataBootstrap } from "@/components/live-data-bootstrap";

const nav = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/recalls", label: "Recalls", icon: Radar },
  { href: "/review", label: "Review Queue", icon: ClipboardCheck },
  { href: "/inventory", label: "Inventory", icon: Boxes },
  { href: "/imports", label: "Imports", icon: Database },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen text-ink">
      <LiveDataBootstrap />
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-80 border-r border-white/10 bg-[#111a16] px-5 py-6 text-white shadow-2xl xl:block">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#f1b650] text-[#111a16] shadow-lg shadow-amber-900/20">
            <Radar className="h-5 w-5" />
          </div>
          <div>
            <div className="text-lg font-black tracking-tight">RecallRadar AI</div>
            <div className="text-xs font-semibold text-emerald-100/70">Food safety operations</div>
          </div>
        </Link>
        <div className="mt-6 rounded-3xl border border-white/10 bg-white/[0.06] p-4">
          <div className="flex items-center gap-2 text-xs font-black uppercase tracking-[0.18em] text-amber-200">
            <ShieldAlert className="h-4 w-4" />
            Live risk desk
          </div>
          <p className="mt-3 text-sm leading-6 text-emerald-50/80">
            Monitor recalls, match inventory, and preserve every decision as evidence.
          </p>
        </div>
        <nav className="mt-7 flex flex-col gap-1">
          {nav.map((item) => (
            <Link key={item.href} href={item.href} className="flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-bold text-emerald-50/70 transition hover:bg-white/10 hover:text-white">
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>
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
        <div className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">{children}</div>
      </main>
    </div>
  );
}
