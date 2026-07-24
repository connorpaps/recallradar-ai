"use client";

import { useRouter, useSearchParams } from "next/navigation";

const filters = {
  source: [
    ["all", "All live recalls"],
    ["live", "Live openFDA"],
  ],
  classification: [
    ["all", "All classes"],
    ["Class I", "Class I"],
    ["Class II", "Class II"],
    ["Class III", "Class III"],
  ],
  has_matches: [
    ["all", "All matches"],
    ["with", "With exposure"],
    ["none", "No matches"],
  ],
};

export function RecallFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();

  function setFilter(key: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value === "all") params.delete(key);
    else params.set(key, value);
    router.push(`/recalls${params.toString() ? `?${params.toString()}` : ""}`);
  }

  return (
    <div className="grid gap-3 rounded-3xl border border-white/70 bg-white/85 p-4 shadow-soft md:grid-cols-3">
      {Object.entries(filters).map(([key, options]) => (
        <select
          key={key}
          value={searchParams.get(key) ?? "all"}
          onChange={(event) => setFilter(key, event.target.value)}
          className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-ink"
          aria-label={key}
        >
          {options.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
      ))}
    </div>
  );
}
