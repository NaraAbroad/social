import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--no-sandbox','--font-render-hinting=none'] });
const p = await b.newPage({ viewport:{width:1080,height:1350}, deviceScaleFactor:1 });
for (const n of ['1-home','2-problem','3-solution']) {
  await p.goto('file://' + process.cwd() + '/' + n + '.html');
  await p.waitForTimeout(700);
  await p.screenshot({ path: n + '.jpg', type:'jpeg', quality:92 });
  console.log('shot', n);
}
await b.close();
