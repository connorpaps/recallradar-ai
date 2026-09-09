"use client";

import { Boxes, ClipboardCheck, Database, LayoutDashboard, Radar } from "lucide-react";
import Link, { type LinkProps } from "next/link";
import { useEffect, useState } from "react";

function useSource() {
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

  return source;
}

function withSource(href: string, source: string | null): string {
  if (source !== "demo") return href;
  return href.includes("?") ? `${href}&source=demo` : `${href}?source=demo`;
}

export function ModeLink({ href, children, ...props }: LinkProps & { children: React.ReactNode; className?: string }) {
  const source = useSource();
  return <Link href={withSource(String(href), source)} {...props}>{children}</Link>;
}

const links = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/recalls", label: "Recalls", icon: Radar },
  { href: "/review", label: "Review Queue", icon: ClipboardCheck },
  { href: "/inventory", label: "Inventory", icon: Boxes },
  { href: "/imports", label: "Imports", icon: Database },
];

export function ModeNavLinks() {
  const source = useSource();
  return (
    <nav className="mt-7 flex flex-col gap-1">
      {links.map((item) => {
        const Icon = item.icon;
        return (
          <Link key={item.href} href={withSource(item.href, source)} className="flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-bold text-emerald-50/70 transition hover:bg-white/10 hover:text-white">
            <Icon className="h-4 w-4" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

export function ModeEvidenceLink({ href, children, ...props }: { href: string; children: React.ReactNode; className?: string }) {
  const source = useSource();
  return <Link href={withSource(href, source)} {...props}>{children}</Link>;
}
