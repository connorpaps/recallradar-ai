import { CheckCircle2, PackagePlus, Radar, RefreshCcw } from "lucide-react";
import { ActionBar } from "@/components/action-bar";
import { CompanySelector } from "@/components/company-selector";
import { CommandHeader } from "@/components/command-header";
import { getDemoCompanies, getImportStatus, getInventory } from "@/lib/api";

const steps = [
  { title: "Auto-refresh FDA recalls", detail: "Recent food enforcement records from openFDA load on full page refresh.", icon: RefreshCcw, tone: "Live" },
  { title: "Choose company inventory", detail: "Realistic stock records with suppliers, UPCs, lots, locations, and criticality.", icon: PackagePlus, tone: "Inventory" },
  { title: "Run matching", detail: "Generate explainable match confidence and operational exposure scores.", icon: Radar, tone: "Analysis" },
  { title: "Review exposure", detail: "Confirm, dismiss, resolve, or reopen live-recall exposure evidence.", icon: CheckCircle2, tone: "Review" },
];

export default async function ImportsPage() {
  const [companies, inventory, importStatus] = await Promise.all([getDemoCompanies(), getInventory(), getImportStatus()]);
  const currentCompany = inventory.items.find((item) => item.raw_row?.demo_company_id)?.raw_row;

  return (
    <div className="flex flex-col gap-6">
      <CommandHeader
        eyebrow="Data operations"
        title="Live data operations"
        description="A guided setup console for live openFDA recall imports, company inventory, and exposure matching."
      />
      <ActionBar companies={companies} selectedCompanyId={typeof currentCompany?.demo_company_id === "string" ? currentCompany.demo_company_id : null} importStatus={importStatus} />
      <CompanySelector companies={companies} selectedCompanyId={typeof currentCompany?.demo_company_id === "string" ? currentCompany.demo_company_id : null} />
      <section className="grid gap-4 lg:grid-cols-4">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <article key={step.title} className="panel p-5">
              <div className="flex items-center justify-between gap-3">
                <div className="rounded-2xl border border-slate-200 bg-field p-3 text-moss">
                  <Icon className="h-5 w-5" />
                </div>
                <div className="text-right">
                  <div className="text-3xl font-black text-slate-200">{index + 1}</div>
                  <div className="text-[0.65rem] font-black uppercase tracking-[0.16em] text-slate-400">{step.tone}</div>
                </div>
              </div>
              <h2 className="mt-5 font-black">{step.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">{step.detail}</p>
            </article>
          );
        })}
      </section>
      <section className="rounded-[1.75rem] border border-[#24382d] bg-[#111a16] p-6 text-white shadow-2xl">
        <p className="text-xs font-black uppercase tracking-[0.22em] text-amber-200">Workflow guidance</p>
        <h2 className="mt-2 text-2xl font-black">Recommended sequence</h2>
        <div className="mt-5 grid gap-3 md:grid-cols-4">
          {["Refresh FDA recalls", "Load company inventory", "Run matching", "Resolve evidence"].map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-white/10 p-4 text-sm font-black">{item}</div>
          ))}
        </div>
        <p className="mt-5 max-w-3xl text-sm font-semibold leading-6 text-emerald-50/70">
          Live openFDA imports provide public recall records. Local inventory remains company seeded or CSV uploaded so exposure matching stays repeatable.
        </p>
      </section>
    </div>
  );
}
