import { chromium } from 'playwright';
const [,, file, out] = process.argv;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
await p.goto('file://' + process.cwd() + '/' + file);
await p.waitForFunction(() => document.fonts.ready.then(() => true));
await p.waitForTimeout(1200);
await p.screenshot({ path: out });
// report any element overflowing the sheet
const bad = await p.evaluate(() => [...document.querySelectorAll('.card,.deck,.band,.head')]
  .filter(e => { const r = e.getBoundingClientRect(); return r.bottom > 1350 || r.right > 1080 || r.left < 0; })
  .map(e => e.className + ' ' + JSON.stringify(e.getBoundingClientRect())));
console.log(bad.length ? 'OVERFLOW:\n' + bad.join('\n') : 'layout ok');
const g = await p.evaluate(() => { const r = document.querySelector('.grid').getBoundingClientRect(); return r.bottom; });
console.log('grid bottom:', g, '/ footer top ~', 1350 - 30 - 100);
await b.close();
