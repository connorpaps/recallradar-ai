"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud } from "lucide-react";
import { API_BASE_URL, postJson } from "@/lib/api";

type UploadPayload = {
  uploaded_file_id: string;
  row_count: number;
  valid_row_count: number;
  invalid_row_count: number;
  errors?: Array<{ row: number; message: string }>;
};

type MatchPayload = {
  created?: number;
  updated?: number;
  skipped?: number;
};

export function InventoryUpload({ source = "openfda" }: { source?: "openfda" | "demo" }) {
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState<Array<{ row: number; message: string }>>([]);
  const [uploadedFileId, setUploadedFileId] = useState<string | null>(null);
  const [isMatching, setIsMatching] = useState(false);

  async function upload(formData: FormData) {
    const file = formData.get("file");
    if (!(file instanceof File) || file.size === 0) {
      setMessage("Choose a CSV file first.");
      return;
    }
    setUploadedFileId(null);
    setMessage("Uploading inventory...");
    try {
      const response = await fetch(`${API_BASE_URL}/inventory/upload`, { method: "POST", body: formData });
      const payload = (await response.json()) as UploadPayload | { detail?: string };
      if (!response.ok) {
        setMessage(`Upload failed: ${"detail" in payload ? payload.detail ?? "check the CSV format" : "check the CSV format"}`);
        setErrors([]);
        return;
      }
      const result = payload as UploadPayload;
      setMessage(`Imported ${result.valid_row_count} of ${result.row_count} rows.`);
      setErrors(result.errors ?? []);
      setUploadedFileId(result.uploaded_file_id);
      router.refresh();
    } catch {
      setMessage("Upload failed: backend unavailable.");
      setErrors([]);
    }
  }

  async function runMatching() {
    if (!uploadedFileId) return;
    setIsMatching(true);
    setMessage("Matching uploaded inventory...");
    try {
      const result = await postJson<MatchPayload>("/matches/run", {
        inventory_upload_id: uploadedFileId,
        min_score: 0.5,
        recall_source: source,
      });
      setMessage(`Matching complete: ${result.created ?? 0} new candidates generated.`);
      router.refresh();
    } catch {
      setMessage("Matching failed: check the active recall data and try again.");
    } finally {
      setIsMatching(false);
    }
  }

  return (
    <form action={upload} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-emerald-50 p-3 text-emerald-700">
          <UploadCloud className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold">Inventory upload</h2>
          <p className="text-sm text-slate-500">CSV columns: product_name, brand, upc, lot_code, quantity, location, supplier, purchase_date</p>
        </div>
      </div>
      <div className="mt-5 flex flex-col gap-3 md:flex-row">
        <input name="file" type="file" accept=".csv" className="w-full rounded-lg border border-slate-200 bg-field px-3 py-2 text-sm" />
        <button className="btn-primary justify-center" type="submit">Upload CSV</button>
        {uploadedFileId ? <button className="btn-secondary justify-center" type="button" disabled={isMatching} onClick={runMatching}>Run matching for uploaded inventory</button> : null}
      </div>
      {message ? <p className="mt-3 text-sm font-semibold text-slate-700">{message}</p> : null}
      {uploadedFileId ? <p className="mt-2 text-xs font-semibold text-slate-500">Upload validated. Matching is a separate reviewable step and has not been run automatically.</p> : null}
      {errors.length ? (
        <div className="mt-4 overflow-hidden rounded-xl border border-amber-200">
          {errors.slice(0, 6).map((error) => (
            <div key={`${error.row}-${error.message}`} className="flex gap-3 border-b border-amber-100 bg-amber-50 px-3 py-2 text-sm text-amber-900 last:border-0">
              <span className="font-bold">Row {error.row}</span>
              <span>{error.message}</span>
            </div>
          ))}
        </div>
      ) : null}
    </form>
  );
}
