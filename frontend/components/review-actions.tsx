"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2, RotateCcw, ShieldCheck, XCircle } from "lucide-react";
import { patchJson } from "@/lib/api";

const actions = [
  { status: "confirmed", label: "Confirm", icon: CheckCircle2 },
  { status: "dismissed", label: "Dismiss", icon: XCircle },
  { status: "resolved", label: "Resolve", icon: ShieldCheck },
  { status: "needs_review", label: "Reopen", icon: RotateCcw },
];

export function ReviewActions({ matchId }: { matchId: string }) {
  const router = useRouter();
  const [isBusy, setIsBusy] = useState(false);

  async function update(status: string) {
    setIsBusy(true);
    await patchJson(`/matches/${matchId}/status`, { status, reviewer_name: "Demo User" });
    setIsBusy(false);
    router.refresh();
  }

  return (
    <div className="flex flex-wrap gap-2">
      {actions.map((action) => (
        <button key={action.status} disabled={isBusy} onClick={() => update(action.status)} className="btn-secondary text-xs">
          <action.icon className="h-3.5 w-3.5" />
          {action.label}
        </button>
      ))}
    </div>
  );
}
