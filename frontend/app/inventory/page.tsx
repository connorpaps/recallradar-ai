import { Boxes, MapPin, Truck } from "lucide-react";
import { CommandHeader } from "@/components/command-header";
import { CompanySelector } from "@/components/company-selector";
import { InventoryUpload } from "@/components/inventory-upload";
import { getDemoCompanies, getInventory } from "@/lib/api";

export default async function InventoryPage() {
  const [inventory, companies] = await Promise.all([getInventory(), getDemoCompanies()]);
  const locations = new Set(inventory.items.map((item) => item.location).filter(Boolean)).size;
  const suppliers = new Set(inventory.items.map((item) => item.supplier).filter(Boolean)).size;
  const currentCompany = inventory.items.find((item) => item.demo_company_id);

  return (
    <div className="flex flex-col gap-6">
      <CommandHeader
        eyebrow="Local stock"
        title="Inventory intelligence"
        description="Upload and inspect local products, suppliers, locations, UPCs, and lot codes before matching against live recall notices."
      >
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="flex items-center gap-2 text-amber-200"><Boxes className="h-4 w-4" /><span className="text-xs font-black uppercase tracking-wide">stock records</span></div>
            <div className="mt-2 text-3xl font-black">{inventory.total}</div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="flex items-center gap-2 text-emerald-100"><MapPin className="h-4 w-4" /><span className="text-xs font-black uppercase tracking-wide">locations</span></div>
            <div className="mt-2 text-3xl font-black">{locations}</div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <div className="flex items-center gap-2 text-emerald-100"><Truck className="h-4 w-4" /><span className="text-xs font-black uppercase tracking-wide">suppliers</span></div>
            <div className="mt-2 text-3xl font-black">{suppliers}</div>
          </div>
        </div>
      </CommandHeader>
      <CompanySelector companies={companies} selectedCompanyId={currentCompany?.demo_company_id ?? null} />
      <InventoryUpload />
      <div className="panel overflow-hidden">
        <div className="border-b border-slate-200 bg-field px-5 py-4">
          <h2 className="font-black">Stock ledger</h2>
          <p className="text-sm text-slate-500">Inventory rows preserve operational context for matching and audit trails.</p>
        </div>
        <div className="hidden grid-cols-12 border-b border-slate-200 bg-white px-4 py-3 text-xs font-black uppercase tracking-wide text-slate-500 md:grid">
          <div className="col-span-4">Product</div>
          <div className="col-span-2">Brand</div>
          <div className="col-span-2">Location</div>
          <div className="col-span-2">Supplier</div>
          <div className="col-span-2">Qty</div>
        </div>
        {inventory.items.map((item) => (
          <div key={item.id} className="grid gap-3 border-b border-slate-100 px-4 py-4 text-sm last:border-0 md:grid-cols-12">
            <div className="md:col-span-4">
              <div className="font-black">{item.product_name}</div>
              <div className="mt-1 text-xs font-semibold text-slate-500">{item.upc ? `UPC ${item.upc}` : "No UPC recorded"} {item.lot_code ? `- Lot ${item.lot_code}` : ""}</div>
              <div className="mt-2 inline-flex rounded-full border border-slate-200 bg-field px-2 py-0.5 text-[0.65rem] font-black uppercase tracking-wide text-slate-500">
                {item.inventory_source === "demo_company" ? item.demo_company_name ?? "Demo company inventory" : "Uploaded inventory"}
              </div>
            </div>
            <div className="text-slate-600 md:col-span-2">{item.brand ?? "Unknown"}</div>
            <div className="text-slate-600 md:col-span-2">{item.location ?? "Unassigned"}</div>
            <div className="text-slate-600 md:col-span-2">{item.supplier ?? "Unknown"}</div>
            <div className="font-semibold md:col-span-2">{item.quantity ?? "-"} {item.unit ?? ""}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
