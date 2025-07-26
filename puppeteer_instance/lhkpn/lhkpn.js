const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();

  // Hide navigator.webdriver
  await context.addInitScript(() => {
    Object.defineProperty(navigator, "webdriver", {
      get: () => false,
    });
  });

  const page = await context.newPage();

  page.on("console", (msg) => console.log("[console]", msg.text()));
  page.on("requestfailed", (request) =>
    console.log("[request failed]", request.url())
  );
  page.on("response", (response) => {
    if (!response.ok()) {
      console.log(`[response ${response.status()}] ${response.url()}`);
    }
  });

  console.log("Navigating to page...");

  await page.goto("https://elhkpn.kpk.go.id/portal/user/login#announ", {
    waitUntil: "networkidle",
    timeout: 30000,
  });

  await page.waitForTimeout(5000); // let modal appear

  // Try to close the modal if it exists
  const closeBtn = await page.$(".modal .close, .popup-close"); // update selector
  if (closeBtn) {
    console.log("Closing modal...");
    await closeBtn.click();
    await page.waitForTimeout(1000);
  }

  await page.screenshot({ path: "page.png" });

  await browser.close();
})();
