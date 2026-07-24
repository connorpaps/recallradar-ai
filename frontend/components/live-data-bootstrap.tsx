"use client";

import { useEffect, useRef } from "react";
import { usePathname, useRouter } from "next/navigation";
import { getImportStatus, postJson } from "@/lib/api";

export function LiveDataBootstrap() {
  const router = useRouter();
  const pathname = usePathname();
  const didRun = useRef(false);

  useEffect(() => {
    if (didRun.current) return;
    didRun.current = true;

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
  }, [pathname, router]);

  return null;
}
