import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";
import { chromium } from "playwright";
import sharp from "sharp";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const slidesDir = path.join(__dirname, "slides");
const outDir = path.join(__dirname, "preview");
const outGrid = path.join(__dirname, "preview-grid.png");

const slideFiles = [
  "slide-01-title.html",
  "slide-02-one-liner.html",
  "slide-03-what-can-do.html",
  "slide-04-constraints.html",
  "slide-05-specialize-compose.html",
  "slide-06-prompt-vs-skill.html",
  "slide-07-use-cases.html"
].map((f) => path.join(slidesDir, f));

const WIDTH = 960;
const HEIGHT = 540;
const COLS = 4;
const GAP = 18;
const LABEL_H = 30;

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function screenshotSlides() {
  await ensureDir(outDir);
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT } });
    const outputs = [];

    for (let i = 0; i < slideFiles.length; i += 1) {
      const htmlFile = slideFiles[i];
      const url = `file://${htmlFile}`;
      const outFile = path.join(outDir, `slide-${String(i + 1).padStart(2, "0")}.png`);
      await page.goto(url);
      await page.waitForTimeout(50);
      await page.screenshot({ path: outFile });
      outputs.push(outFile);
    }

    return outputs;
  } finally {
    await browser.close();
  }
}

async function makeGrid(images) {
  const rows = Math.ceil(images.length / COLS);
  const gridW = COLS * WIDTH + (COLS + 1) * GAP;
  const gridH = rows * (HEIGHT + LABEL_H) + (rows + 1) * GAP;

  const base = sharp({
    create: {
      width: gridW,
      height: gridH,
      channels: 4,
      background: { r: 20, g: 23, b: 32, alpha: 1 }
    }
  });

  const composites = [];
  for (let idx = 0; idx < images.length; idx += 1) {
    const row = Math.floor(idx / COLS);
    const col = idx % COLS;
    const x = GAP + col * (WIDTH + GAP);
    const y = GAP + row * (HEIGHT + LABEL_H + GAP);

    composites.push({ input: await sharp(images[idx]).png().toBuffer(), left: x, top: y });

    const labelSvg = Buffer.from(
      `<svg width="${WIDTH}" height="${LABEL_H}" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="${WIDTH}" height="${LABEL_H}" fill="#23283A"/>
        <text x="12" y="20" font-family="Arial, Helvetica, sans-serif" font-size="16" fill="#E7ECFF">Slide ${idx + 1}</text>
      </svg>`
    );
    composites.push({ input: labelSvg, left: x, top: y + HEIGHT });
  }

  await base.composite(composites).png().toFile(outGrid);
  // eslint-disable-next-line no-console
  console.log(outGrid);
}

async function main() {
  const images = await screenshotSlides();
  await makeGrid(images);
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exitCode = 1;
});

