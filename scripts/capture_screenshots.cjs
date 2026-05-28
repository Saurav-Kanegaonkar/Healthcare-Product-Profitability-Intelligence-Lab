const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const IMAGE_DIR = path.join(ROOT, "docs", "images");

async function capture() {
  fs.mkdirSync(IMAGE_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 960 }, deviceScaleFactor: 1 });
  await page.goto("http://localhost:4183", { waitUntil: "networkidle" });

  await page.screenshot({ path: path.join(IMAGE_DIR, "profitability-command-center.png"), fullPage: false });
  await page.getByRole("button", { name: "Market" }).click();
  await page.screenshot({ path: path.join(IMAGE_DIR, "market-pricing-strategy.png"), fullPage: false });
  await page.getByRole("button", { name: "Research" }).click();
  await page.screenshot({ path: path.join(IMAGE_DIR, "research-evidence.png"), fullPage: false });

  await browser.close();
  console.log("Captured portfolio artifact screenshots.");
}

capture().catch((error) => {
  console.error(error);
  process.exit(1);
});
