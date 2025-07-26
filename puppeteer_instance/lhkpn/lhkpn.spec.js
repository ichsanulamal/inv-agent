import { test, expect } from "@playwright/test";

test("search e-Announcement", async ({ page }) => {
  // Log traffic for debug
  page.on("request", (req) => console.log("➡️", req.method(), req.url()));
  page.on("response", (res) => console.log("⬅️", res.status(), res.url()));

  // Go directly to the search page
  await page.goto(
    "https://elhkpn.kpk.go.id/portal/user/check_search_announ#announ",
    {
      waitUntil: "networkidle",
    }
  );

  // Fill in "Cari" field
  const cariBox = page.getByPlaceholder("Nama/NIK");
  await cariBox.waitFor({ state: "visible" });
  await cariBox.fill("prabowo subianto");

  // Click the green search button
  await page.locator('button:has-text("")').click();

  // Wait for table or known result text
  await page.waitForSelector("text=PRABOWO SUBIANTO", { timeout: 10000 });

  // Screenshot result
  await page.screenshot({ path: "announcement-result.png", fullPage: true });

  // Optional: extract rows
  const rows = await page.$$eval("table.table tbody tr", (trs) =>
    trs.map((tr) => [...tr.querySelectorAll("td")].map((td) => td.innerText))
  );

  console.log("🧾 Found rows:", rows);
});
