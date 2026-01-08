import path from "path";
import { fileURLToPath } from "url";
import { createRequire } from "module";
import pptxgen from "pptxgenjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const html2pptxPath = path.join(__dirname, "html2pptx.js");
const require = createRequire(import.meta.url);
const html2pptx = require(html2pptxPath);

const slidesDir = path.join(__dirname, "slides");
const outFile = path.join(path.dirname(__dirname), "2.pptx");

const slideFiles = [
  "slide-01-title.html",
  "slide-02-one-liner.html",
  "slide-03-what-can-do.html",
  "slide-04-constraints.html",
  "slide-05-specialize-compose.html",
  "slide-06-prompt-vs-skill.html",
  "slide-07-use-cases.html"
].map((f) => path.join(slidesDir, f));

async function main() {
  const pptx = new pptxgen();
  pptx.layout = "LAYOUT_16x9";

  for (const htmlFile of slideFiles) {
    await html2pptx(htmlFile, pptx);
  }

  await pptx.writeFile({ fileName: outFile });
  console.log(outFile);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
