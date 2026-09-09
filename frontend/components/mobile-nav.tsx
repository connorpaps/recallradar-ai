"use client";

import { Boxes, ClipboardCheck, Database, LayoutDashboard, Menu, Radar, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const links = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/recalls", label: "Recalls", icon: Radar },
  { href: "/review", label: "Review Queue", icon: ClipboardCheck },
  { href: "/inventory", label: "Inventory", icon: Boxes },
  { href: "/imports", label: "Imports", icon: Database },
];

export function MobileNav() {
  const [open, setOpen] = useState(false);
  const [source, setSource] = useState<string | null>(null);

  useEffect(() => {
    const syncSource = () => setSource(new URLSearchParams(window.location.search).get("source"));
    syncSource();
    window.addEventListener("popstate", syncSource);
    window.addEventListener("recallradar:url-change", syncSource);
    return () => {
      window.removeEventListener("popstate", syncSource);
      window.removeEventListener("recallradar:url-change", syncSource);
    };
  }, []);

  const homeHref = source === "demo" ? "/?source=demo" : "/";

  return (
    <div className="mb-4 xl:hidden">
      <div className="flex items-center justify-between rounded-3xl border border-white/70 bg-white/90 p-3 shadow-soft">
        <Link href={homeHref} className="text-sm font-black text-ink">RecallRadar AI</Link>
        <button
          type="button"
          aria-label={open ? "Close navigation" : "Open navigation"}
          onClick={() => setOpen((value) => !value)}
          className="rounded-2xl border border-slate-200 bg-white p-2 text-ink"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>
      {open ? (
        <nav aria-label="Mobile navigation" className="mt-2 grid gap-1 rounded-3xl border border-slate-200 bg-white p-2 shadow-soft">
          {links.map((link) => {
            const Icon = link.icon;
            const href = source === "demo" ? `${link.href}?source=demo` : link.href;
            return <Link key={link.href} href={href} onClick={() => setOpen(false)} className="flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-bold text-ink hover:bg-field"><Icon className="h-4 w-4 text-moss" />{link.label}</Link>;
          })}
        </nav>
      ) : null}
    </div>
  );
}
