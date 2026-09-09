"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { getImportStatus, postJson } from "@/lib/api";

export function LiveDataBootstrap() {
  const router = useRouter();
  const pathname = usePathname();
  const [mode, setMode] = useState<"demo" | "live">(() => (
    typeof window !== "undefined" && new URLSearchParams(window.location.search).get("source") === "demo" ? "demo" : "live"
  ));

  useEffect(() => {
    const syncMode = () => setMode(new URLSearchParams(window.location.search).get("source") === "demo" ? "demo" : "live");
    syncMode();
    window.addEventListener("popstate", syncMode);
    window.addEventListener("recallradar:url-change", syncMode);
    return () => {
      window.removeEventListener("popstate", syncMode);
      window.removeEventListener("recallradar:url-change", syncMode);
    };
  }, []);

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_ENABLE_LIVE_REFRESH === "false") return;
    if (mode === "demo") return;

    getImportStatus()
      .then(async (status) => {
        if (!status.should_refresh) return false;
        window.dispatchEvent(new CustomEvent("recallradar:import-status", { detail: { status: "running" } }));
        await postJson("/recalls/import/openfda", { limit: 50 });
        return true;
      })
      .then((didRefresh) => {
        if (!didRefresh) return;
        window.dispatchEvent(new CustomEvent("recallradar:import-status", { detail: { status: "succeeded" } }));
        if (pathname !== "/inventory") router.refresh();
      })
      .catch((error) => {
        window.dispatchEvent(new CustomEvent("recallradar:import-status", { detail: { status: "failed", error: error instanceof Error ? error.message : "Live import failed." } }));
      });
  }, [mode, pathname, router]);

  return null;
}
