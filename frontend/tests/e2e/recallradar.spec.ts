import { expect, test, type Page } from "@playwright/test";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8100";

async function api(path: string, init?: RequestInit) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    throw new Error(`${path} failed: ${response.status} ${await response.text()}`);
  }
  return response.json();
}

async function apiAllowConflict(path: string, init?: RequestInit) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok && response.status !== 409) {
    throw new Error(`${path} failed: ${response.status} ${await response.text()}`);
  }
  return response.ok ? response.json() : null;
}

async function seedWorkflow() {
  await apiAllowConflict("/inventory/seed-company", {
    method: "POST",
    body: JSON.stringify({ company_id: "metro_mart_grocery" }),
  });
  await apiAllowConflict("/demo/portfolio", { method: "POST", body: "{}" });
  const recalls = await api("/recalls?source=demo&page_size=1");
  if (recalls.items.length === 0) throw new Error("Portfolio Demo fixture is unavailable after seed conflict");
}

async function expectStylesheetLoads(page: Page) {
  const stylesheet = await page.locator('link[rel="stylesheet"]').first().getAttribute("href");
  expect(stylesheet).toBeTruthy();
  const cssUrl = new URL(stylesheet!, page.url()).toString();
  const cssResponse = await page.request.get(cssUrl);
  expect(cssResponse.status()).toBe(200);
}

test.beforeAll(async () => {
  await seedWorkflow();
});

test("[mobile-safe] primary routes load with styled app shell", async ({ page }) => {
  const liveImportRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/recalls/import/openfda")) liveImportRequests.push(request.url());
  });
  await page.goto("/?source=demo");
  await expect(page.getByRole("heading", { name: /Food safety intelligence/ })).toBeVisible();
  await expect(page.getByLabel("company inventory")).toBeVisible();
  await expect(page.getByText(/Last FDA refresh|FDA recalls refreshed|No successful refresh yet/)).toBeVisible();

  await expectStylesheetLoads(page);

  const routes = [
    { path: "/recalls?source=demo", heading: /Active recall worklist/ },
    { path: "/review?source=demo", heading: /Evidence triage queue/ },
    { path: "/inventory?source=demo", heading: /Inventory intelligence/ },
    { path: "/imports?source=demo", heading: /Live data operations/ },
  ];
  for (const route of routes) {
    await page.goto(route.path);
    await expect(page.getByRole("heading", { name: route.heading })).toBeVisible();
  }

  await page.goto("/?source=demo");
  if (test.info().project.name === "chromium") {
    await expect(page.locator('a[href*="/recalls/"][href*="source=demo"]').first()).toBeVisible();
  }
  const recalls = await api("/recalls?page_size=1&source=demo");
  await page.goto(`/recalls/${recalls.items[0].id}?source=demo`);
  await expect(page.getByText("Recall case file")).toBeVisible();
  await expect(page.getByText("AI support")).toBeVisible();
  expect(liveImportRequests).toEqual([]);
});

test("[mobile-safe] primary route CSS assets load", async ({ page }) => {
  for (const path of ["/?source=demo", "/recalls?source=demo", "/review?source=demo", "/inventory?source=demo", "/imports?source=demo"]) {
    await page.goto(path);
    await expectStylesheetLoads(page);
  }
});

test("review actions confirm dismiss resolve and reopen", async ({ page }) => {
  await apiAllowConflict("/demo/portfolio", { method: "POST", body: "{}" });
  await page.goto("/review?source=demo");
  const matches = await api("/matches?status=needs_review&recall_source=demo&page_size=1");
  expect(matches.items.length).toBeGreaterThan(0);
  const matchId = matches.items[0].id;

  for (const status of ["confirmed", "dismissed", "resolved", "needs_review"]) {
    const result = await api(`/matches/${matchId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, reviewer_name: "Playwright" }),
    });
    expect(result.status).toBe(status);
  }

  await page.reload();
  await expect(page.getByText("Evidence triage queue")).toBeVisible();
});

test("portfolio demo mode loads deterministic evidence", async ({ page }) => {
  await apiAllowConflict("/demo/portfolio", { method: "POST", body: "{}" });
  await page.goto("/?source=demo");
  await expect(page.getByText("Portfolio demo mode")).toBeVisible();
  await expect(page.getByText("10 demo recalls")).toBeVisible();
  await expect(page.getByText("5 high-confidence")).toBeVisible();
  await expect(page.getByText("3 medium-confidence")).toBeVisible();
});

test("company selector replaces inventory", async ({ page }) => {
  await page.goto("/inventory");
  await expect(page.getByText("Demo company inventory")).toBeVisible();
  const inventory = await api("/inventory?page_size=100");
  const hasUploadedInventory = inventory.items.some((item: { demo_company_id?: string | null }) => !item.demo_company_id);
  await page.getByRole("button", { name: /Oak & Ember Steakhouse/ }).click();
  if (hasUploadedInventory) {
    await expect(page.getByText(/will not replace uploaded inventory/)).toBeVisible();
  } else {
    await expect(page.getByText(/Oak & Ember Steakhouse loaded/)).toBeVisible();
    await expect(page.getByText("Oak & Ember Steakhouse").first()).toBeVisible();
  }
});

test("command bar can load company inventory", async ({ page }) => {
  await page.goto("/?source=demo");
  const inventory = await api("/inventory?page_size=100");
  const hasUploadedInventory = inventory.items.some((item: { demo_company_id?: string | null }) => !item.demo_company_id);
  await page.getByLabel("company inventory").selectOption("campus_table_dining");
  if (hasUploadedInventory) {
    await expect(page.getByText(/will not replace uploaded inventory/)).toBeVisible();
  } else {
    await expect(page.getByText(/Campus Table Dining loaded/)).toBeVisible();
  }
});

test("recall filters expose live controls", async ({ page }) => {
  await page.goto("/recalls?source=demo");
  await expect(page.getByLabel("source")).toHaveValue("demo");
  await expect(page.getByLabel("source")).toContainText("Portfolio Demo");
  await page.getByLabel("classification").selectOption("Class I");
  await expect(page).toHaveURL(/classification=Class\+I/);
  await page.getByLabel("has_matches").selectOption("with");
  await expect(page).toHaveURL(/has_matches=with/);
});

test("CSV upload exposes an explicit matching next step", async ({ page }) => {
  await page.goto("/inventory?source=demo");
  await page.locator('input[type="file"]').setInputFiles({
    name: "portfolio-upload.csv",
    mimeType: "text/csv",
    buffer: Buffer.from("product_name,brand,quantity\nBlue Kettle Creamy Peanut Butter,Blue Kettle,12\nUnrelated Demo Product,Example,4\n"),
  });
  await page.getByRole("button", { name: "Upload CSV" }).click();
  await expect(page.getByText("Imported 2 of 2 rows.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Run matching for uploaded inventory" })).toBeVisible();
  const matchingRequest = page.waitForRequest((request) => request.url().endsWith("/matches/run") && request.method() === "POST");
  await page.getByRole("button", { name: "Run matching for uploaded inventory" }).click();
  expect(JSON.parse((await matchingRequest).postData() ?? "{}").recall_source).toBe("demo");
  await expect(page.getByText(/Matching complete/)).toBeVisible();
});

test("[mobile-safe] mobile navigation exposes primary routes", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/?source=demo");
  await expect(page.getByRole("button", { name: "Open navigation" })).toBeVisible();
  await page.getByRole("button", { name: "Open navigation" }).click();
  await expect(page.getByRole("link", { name: "Recalls" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Inventory" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Review Queue" })).toHaveAttribute("href", "/review?source=demo");
});
