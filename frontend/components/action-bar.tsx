"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, Play, RefreshCcw, Sparkles } from "lucide-react";
import { postJson } from "@/lib/api";
import type { DemoCompany, ImportStatus } from "@/types/api";

type OperationResult = {
  created?: number;
  imported?: number;
  updated?: number;
  skipped?: number;
  company?: DemoCompany;
  matches_created?: number;
  high_confidence_matches?: number;
  medium_confidence_matches?: number;
};

function formatRefreshTime(value?: string | null): string {
  if (!value) return "No successful refresh yet";
  const date = new Date(value);
  const formatted = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZone: "UTC",
    timeZoneName: "short",
  }).format(date);
  return `Last FDA refresh ${formatted}`;
}

export function ActionBar({
  companies = [],
  selectedCompanyId,
  importStatus,
  source = "openfda",
}: {
  companies?: DemoCompany[];
  selectedCompanyId?: string | null;
  importStatus?: ImportStatus | null;
  source?: "openfda" | "demo";
}) {
  const router = useRouter();
  const [message, setMessage] = useState<string>("");
  const [lastResult, setLastResult] = useState<string>("");
  const [isBusy, setIsBusy] = useState(false);
  const [companyId, setCompanyId] = useState(selectedCompanyId ?? "");
  const [liveStatus, setLiveStatus] = useState(importStatus?.status ?? "idle");
  const [liveStatusText, setLiveStatusText] = useState(formatRefreshTime(importStatus?.last_success_at));

  useEffect(() => {
    const listener = (event: Event) => {
      const detail = (event as CustomEvent<{ status?: string; error?: string }>).detail;
      if (!detail?.status) return;
      setLiveStatus(detail.status);
      if (detail.status === "running") setLiveStatusText("Refreshing FDA recalls...");
      if (detail.status === "succeeded") setLiveStatusText("FDA recalls refreshed");
      if (detail.status === "failed") setLiveStatusText(detail.error ?? "FDA refresh failed");
    };
    window.addEventListener("recallradar:import-status", listener);
    return () => window.removeEventListener("recallradar:import-status", listener);
  }, []);

  function formatResult(result: unknown): string {
    if (!result || typeof result !== "object") {
      return "";
    }
    const values = result as OperationResult;
    return [
      values.company?.name ? `${values.company.name} loaded` : "",
      values.created !== undefined ? `${values.created} created` : "",
      values.imported !== undefined ? `${values.imported} imported` : "",
      values.updated !== undefined ? `${values.updated} updated` : "",
      values.skipped !== undefined ? `${values.skipped} skipped` : "",
      values.matches_created !== undefined ? `${values.matches_created} matches` : "",
    ].filter(Boolean).join(" / ");
  }

  async function selectCompany(nextCompanyId: string) {
    setCompanyId(nextCompanyId);
    const company = companies.find((item) => item.id === nextCompanyId);
    await run(
      company ? `Loading ${company.name}` : "Loading company inventory",
      () => postJson("/inventory/seed-company", { company_id: nextCompanyId }),
    );
  }

  async function run(label: string, action: () => Promise<unknown>) {
    setIsBusy(true);
    setMessage(`${label}...`);
    setLastResult("");
    try {
      const result = await action();
      setMessage(`${label} complete`);
      setLastResult(formatResult(result));
      if (label.includes("FDA")) {
        setLiveStatus("succeeded");
        setLiveStatusText("FDA recalls refreshed");
      }
      router.refresh();
    } catch (error) {
      setMessage(`${label} failed`);
      setLastResult(error instanceof Error ? error.message : "Check backend logs for details.");
      if (label.includes("FDA")) {
        setLiveStatus("failed");
        setLiveStatusText("FDA refresh failed");
      }
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <div className="mb-6 flex flex-col gap-4 rounded-3xl border border-white/70 bg-white/85 p-4 shadow-soft backdrop-blur md:flex-row md:items-center md:justify-between">
      <div>
        <p className="text-sm font-black text-ink">Operations command center</p>
        <p className="mt-1 text-xs font-semibold text-slate-500">{message || "Choose a data mode, load inventory, and run reviewable matching from one place."}</p>
        <p className={`mt-1 text-xs font-black ${liveStatus === "failed" ? "text-red-600" : liveStatus === "running" ? "text-amber-600" : "text-moss"}`}>{liveStatusText}</p>
        {lastResult ? <p className="mt-1 text-xs font-black text-moss">{lastResult}</p> : null}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <button disabled={isBusy} onClick={() => run("Importing FDA recalls", () => postJson("/recalls/import/openfda", { limit: 50, force: true }))} className="btn-secondary">
          <RefreshCcw className="h-4 w-4" /> Live FDA import
        </button>
        <button disabled={isBusy} onClick={() => run("Loading portfolio demo", async () => {
          const result = await postJson("/demo/portfolio", {});
          router.push("/?source=demo");
          return result;
        })} className="btn-secondary">
          <Sparkles className="h-4 w-4" /> Portfolio demo
        </button>
        <label className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-ink shadow-sm">
          <Building2 className="h-4 w-4 text-moss" />
          <select
            disabled={isBusy || !companies.length}
            value={companyId}
            onChange={(event) => selectCompany(event.target.value)}
            className="bg-transparent text-sm font-bold outline-none disabled:opacity-60"
            aria-label="company inventory"
          >
            <option value="" disabled>Choose company</option>
            {companies.map((company) => <option key={company.id} value={company.id}>{company.name}</option>)}
          </select>
        </label>
        <button disabled={isBusy} onClick={() => run("Running matching", () => postJson("/matches/run", { min_score: 0.5, recall_source: source }))} className="btn-primary">
          <Play className="h-4 w-4" /> Run matching
        </button>
      </div>
    </div>
  );
}
