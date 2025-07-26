const { chromium } = require("playwright"); // Or import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launchPersistentContext(
    "/home/al/.config/google-chrome/Default",
    {
      headless: false,
      args: ["--start-maximized"],
    }
  );

  const page = await browser.newPage();
  await page.goto("https://elhkpn.kpk.go.id/portal/user/login#announ");

  // Click the 'e-Announcement' link
  await page.click('a[href="#announ"]');

  // Wait for input to appear
  await page.waitForSelector("#CARI_NAMA");
  await page.fill("#CARI_NAMA", "prabowo");
  await page.keyboard.press("Enter");

  // Wait for results
  await page.waitForSelector("#announ-page table");

  // Screenshot the result
  await page.screenshot({ path: "result.png", fullPage: true });

  console.log("✅ Done. Screenshot saved as result.png");
})();
