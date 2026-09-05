import { chromium } from 'playwright';
import { mkdirSync, rmSync } from 'fs';
const FPS = 30, DUR = 26, N = FPS * DUR;
rmSync('frames-paper', { recursive: true, force: true }); mkdirSync('frames-paper');
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args:['--no-sandbox','--font-render-hinting=none'] });
const p = await b.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
await p.goto('file://' + process.cwd() + '/paper.html');
await p.waitForTimeout(1200);
for (let i = 0; i < N; i++) {
  await p.evaluate(t => window.render(t), i / FPS);
  await p.screenshot({ path:`frames-paper/f${String(i).padStart(4,'0')}.jpg`, type:'jpeg', quality:94 });
  if (i % 150 === 0) console.log(`  ${i}/${N}`);
}
await b.close(); console.log('frames done');
