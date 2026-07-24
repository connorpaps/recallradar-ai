"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud } from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

export function InventoryUpload() {
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState<Array<{ row: number; message: string }>>([]);

  async function upload(formData: FormData) {
    const file = formData.get("file");
    if (!(file instanceof File) || file.size === 0) {
      setMessage("Choose a CSV file first.");
      return;
    }
    const response = await fetch(`${API_BASE_URL}/inventory/upload`, { method: "POST", body: formData });
    const payload = await response.json();
    if (!response.ok) {
      setMessage("Upload failed.");
      return;
    }
    setMessage(`Imported ${payload.valid_row_count} of ${payload.row_count} rows.`);
    setErrors(payload.errors ?? []);
    router.refresh();
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
      </div>
      {message ? <p className="mt-3 text-sm font-semibold text-slate-700">{message}</p> : null}
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
