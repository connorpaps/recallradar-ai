import { expect, test, type Page } from "@playwright/test";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

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

async function seedWorkflow() {
  await api("/recalls/import/openfda", { method: "POST", body: JSON.stringify({ limit: 50 }) });
  await api("/inventory/seed", { method: "POST", body: "{}" });
  await api("/matches/run", { method: "POST", body: JSON.stringify({ min_score: 0.35 }) });
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

test("primary routes load with styled app shell", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Food safety intelligence/ })).toBeVisible();
  await expect(page.getByLabel("company inventory")).toBeVisible();
  await expect(page.getByText(/Last FDA refresh|FDA recalls refreshed|No successful refresh yet/)).toBeVisible();

  await expectStylesheetLoads(page);

  const routes = [
    { path: "/recalls", heading: /Active recall worklist/ },
    { path: "/review", heading: /Evidence triage queue/ },
    { path: "/inventory", heading: /Inventory intelligence/ },
    { path: "/imports", heading: /Live data operations/ },
  ];
  for (const route of routes) {
    await page.goto(route.path);
    await expect(page.getByRole("heading", { name: route.heading })).toBeVisible();
  }

  const recalls = await api("/recalls?page_size=1");
  await page.goto(`/recalls/${recalls.items[0].id}`);
  await expect(page.getByText("Recall case file")).toBeVisible();
  await expect(page.getByText("AI support")).toBeVisible();
});

test("primary route CSS assets load", async ({ page }) => {
  for (const path of ["/", "/recalls", "/review", "/inventory", "/imports"]) {
    await page.goto(path);
    await expectStylesheetLoads(page);
  }
});

test("review actions confirm dismiss resolve and reopen", async ({ page }) => {
  await page.goto("/review");
  const matches = await api("/matches?status=needs_review&page_size=1");
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

test("company selector replaces inventory", async ({ page }) => {
  await page.goto("/inventory");
  await expect(page.getByText("Demo company inventory")).toBeVisible();
  await page.getByRole("button", { name: /Oak & Ember Steakhouse/ }).click();
  await expect(page.getByText(/Oak & Ember Steakhouse loaded/)).toBeVisible();
  await expect(page.getByText("Oak & Ember Steakhouse").first()).toBeVisible();
});

test("command bar can load company inventory", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("company inventory").selectOption("campus_table_dining");
  await expect(page.getByText(/Campus Table Dining loaded/)).toBeVisible();
});

test("recall filters expose live controls", async ({ page }) => {
  await page.goto("/recalls");
  await expect(page.getByLabel("source")).not.toContainText("Demo recalls");
  await page.getByLabel("classification").selectOption("Class I");
  await expect(page).toHaveURL(/classification=Class\+I/);
  await page.getByLabel("has_matches").selectOption("with");
  await expect(page).toHaveURL(/has_matches=with/);
});
