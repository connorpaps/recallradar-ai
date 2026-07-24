"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, CheckCircle2 } from "lucide-react";
import { postJson } from "@/lib/api";
import type { DemoCompany } from "@/types/api";

export function CompanySelector({ companies, selectedCompanyId }: { companies: DemoCompany[]; selectedCompanyId?: string | null }) {
  const router = useRouter();
  const [busyCompanyId, setBusyCompanyId] = useState<string | null>(null);
  const [message, setMessage] = useState("");

  async function selectCompany(company: DemoCompany) {
    setBusyCompanyId(company.id);
    setMessage("");
    try {
      const result = await postJson<{ created: number; company: DemoCompany }>("/inventory/seed-company", { company_id: company.id });
      setMessage(`${result.company.name} loaded with ${result.created} inventory rows. Existing matches were cleared.`);
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Company load failed.");
    } finally {
      setBusyCompanyId(null);
    }
  }

  return (
    <section className="panel overflow-hidden">
      <div className="border-b border-slate-200 bg-field px-5 py-4">
        <h2 className="font-black">Demo company inventory</h2>
        <p className="text-sm text-slate-500">Pick a realistic operating environment. Loading a company replaces current inventory and clears matches.</p>
        {message ? <p className="mt-2 text-xs font-black text-moss">{message}</p> : null}
      </div>
      <div className="grid gap-3 p-4 lg:grid-cols-4">
        {companies.map((company) => {
          const isSelected = selectedCompanyId === company.id;
          const isBusy = busyCompanyId === company.id;
          return (
            <button
              key={company.id}
              type="button"
              disabled={Boolean(busyCompanyId)}
              onClick={() => selectCompany(company)}
              className="rounded-2xl border border-slate-200 bg-white p-4 text-left transition hover:-translate-y-0.5 hover:shadow-soft disabled:opacity-60"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="rounded-xl border border-slate-200 bg-field p-2 text-moss"><Building2 className="h-4 w-4" /></div>
                {isSelected ? <CheckCircle2 className="h-5 w-5 text-emerald-600" /> : null}
              </div>
              <div className="mt-3 text-sm font-black">{company.name}</div>
              <div className="mt-1 text-xs font-black uppercase tracking-wide text-slate-400">{company.company_type}</div>
              <p className="mt-2 line-clamp-3 text-xs font-semibold leading-5 text-slate-500">{company.description}</p>
              <div className="mt-3 text-xs font-black text-moss">{isBusy ? "Loading..." : `${company.item_count} stock rows`}</div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
