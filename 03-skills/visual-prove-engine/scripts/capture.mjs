// Node Playwright backend for `vqa capture`.
// Resolves `playwright` from process.cwd() (the product repo), not this skill.
import { chromium } from 'playwright';

const url = process.env.VQA_CAPTURE_URL;
const out = process.env.VQA_CAPTURE_OUT;
if (!url || !out) {
  console.error('VQA_CAPTURE_URL and VQA_CAPTURE_OUT are required');
  process.exit(2);
}

const viewport = {
  width: Number(process.env.VQA_CAPTURE_WIDTH ?? 1920),
  height: Number(process.env.VQA_CAPTURE_HEIGHT ?? 1080),
};
const dpr = Number(process.env.VQA_CAPTURE_DPR ?? 2);
const waitMs = Number(process.env.VQA_CAPTURE_WAIT_MS ?? 1000);
const fullPage = process.env.VQA_CAPTURE_FULL_PAGE === '1';
const reducedMotion = process.env.VQA_CAPTURE_REDUCED_MOTION !== '0';

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport,
  deviceScaleFactor: dpr,
  ...(reducedMotion ? { reducedMotion: 'reduce' } : {}),
});
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
await page.waitForTimeout(waitMs);
await page.screenshot({ path: out, fullPage });
await browser.close();
console.log('wrote', out);
