import { chromium } from 'playwright';
import { writeFileSync } from 'fs';
import { posts } from './posts.mjs';

const THEMES = {
  dark:{ bg:`radial-gradient(1200px 700px at 88% -12%, #1D3E70 0%, transparent 60%),
             radial-gradient(900px 600px at 5% 108%, #14305C 0%, transparent 58%),
             linear-gradient(168deg,#0A1A33 0%,#0C2044 100%)`,
    fg:'#fff', accent:'#F0B429', muted:'#9FB6D6', soft:'#C6D6EC',
    line:'rgba(255,255,255,.16)', chipBg:'rgba(240,180,41,.14)', chipBd:'rgba(240,180,41,.32)',
    panel:'rgba(255,255,255,.05)', panelBd:'rgba(255,255,255,.10)',
    grain:'rgba(255,255,255,.10)', onAccent:'#0A1A33' },
  light:{ bg:`radial-gradient(900px 620px at 92% 6%, #F6E2DE 0%, transparent 62%),
              linear-gradient(172deg,#FBF8F2 0%,#F3ECE1 100%)`,
    fg:'#0A1A33', accent:'#E4574C', muted:'#5A6E8C', soft:'#22344F',
    line:'rgba(10,26,51,.16)', chipBg:'rgba(228,87,76,.12)', chipBd:'rgba(228,87,76,.30)',
    panel:'rgba(10,26,51,.04)', panelBd:'rgba(10,26,51,.10)',
    grain:'rgba(10,26,51,.07)', onAccent:'#fff' },
  paper:{ bg:`radial-gradient(900px 620px at 88% 4%, #F3E9D6 0%, transparent 60%),
              radial-gradient(760px 560px at 4% 100%, #EDE4D2 0%, transparent 58%),
              linear-gradient(170deg,#FAF4E8 0%,#F2E9D8 100%)`,
    fg:'#26262A', accent:'#2A5570', muted:'#6E6A5F', soft:'#3A3A36',
    line:'rgba(38,38,42,.18)', chipBg:'rgba(42,85,112,.10)', chipBd:'rgba(42,85,112,.30)',
    panel:'rgba(38,38,42,.04)', panelBd:'rgba(38,38,42,.10)',
    grain:'rgba(38,38,42,.10)', onAccent:'#FAF4E8' },
  deep:{ bg:`radial-gradient(1000px 640px at 10% -8%, #164A47 0%, transparent 60%),
             radial-gradient(880px 620px at 96% 104%, #123B62 0%, transparent 58%),
             linear-gradient(168deg,#08202E 0%,#0A1A33 100%)`,
    fg:'#fff', accent:'#3FBF9A', muted:'#9FB6D6', soft:'#E4EEF6',
    line:'rgba(255,255,255,.16)', chipBg:'rgba(63,191,154,.14)', chipBd:'rgba(63,191,154,.34)',
    panel:'rgba(255,255,255,.05)', panelBd:'rgba(255,255,255,.10)',
    grain:'rgba(255,255,255,.10)', onAccent:'#08202E' },
};

const esc = s => s ?? '';
const AR = /[\u0600-\u06FF]/;
const nm = v => AR.test(String(v)) ? v : `<span class="ltr">${v}</span>`;
const hsize = h => { const n = h.replace(/<[^>]+>/g,'').length; return n>34?78:n>26?88:96; };

function render(p){
  const t = THEMES[p.theme];
  const dense = (p.rows && p.rows.length >= 4) || (p.list && p.list.length >= 5);
  const denseCSS = dense ? `
.rows{margin-top:26px;gap:12px}
.row{padding:18px 26px}
.rk,.rv{font-size:30px}
.rn{font-size:22px}
.list{margin-top:26px;gap:18px}
.tx{font-size:29px}
h1{font-size:76px}
.note{margin-top:28px;font-size:27px}
.src{margin-top:18px}` : '';
  const blocks = [`<h1>${p.h}</h1>`];
  if (p.kicker) blocks.push(`<p class="kicker">${p.kicker}</p>`);
  if (p.big) blocks.push(`<div class="big"><span class="from">${nm(p.big.from)}</span>
      <span class="arrow">←</span><span class="to">${nm(p.big.to)}</span></div>`);
  if (p.stats) blocks.push(`<div class="stats ${p.stats.length>2?'s3':''}">` + p.stats.map(s =>
      `<div class="stat"><div class="num">${nm(s.n)}</div><div class="lbl">${s.l}</div></div>`).join('') + `</div>`);
  if (p.rows) blocks.push(`<div class="rows">` + p.rows.map(r =>
      `<div class="row ${r.hl?'hl':''}"><div class="rk">${r.k}</div>
       <div class="rv">${nm(r.v)}</div><div class="rn">${r.n}</div></div>`).join('') + `</div>`);
  if (p.list) blocks.push(`<div class="list">` + p.list.map(i =>
      `<div class="item"><div class="mk">${i.m}</div><div class="tx">${i.t}</div></div>`).join('') + `</div>`);
  if (p.note) blocks.push(`<p class="note">${p.note}</p>`);

  return `<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<link rel="stylesheet" href="base.css"><style>
.card{background:${t.bg};color:${t.fg}}
.grain{background-image:radial-gradient(circle at 1px 1px, ${t.grain} 1px, transparent 0)}
.deco{position:absolute;border-radius:50%;border:2px solid ${t.chipBd};
  width:1020px;height:1020px;top:-400px;left:-300px;opacity:.75}
.tag{background:${t.chipBg};color:${t.accent};border:1px solid ${t.chipBd};font-size:19px}
h1{font-size:${hsize(p.h)}px}
h1 em{font-style:normal;color:${t.accent}}
.kicker{margin-top:26px;font-size:34px;line-height:1.55;font-weight:600;color:${t.soft};max-width:850px}
.big{display:flex;align-items:center;gap:34px;margin-top:44px;flex-wrap:nowrap}
.from{font-size:60px;font-weight:900;color:${t.muted};text-decoration:line-through;
  text-decoration-thickness:3px;white-space:nowrap;opacity:.75}
.arrow{font-size:52px;color:${t.accent};font-weight:900}
.to{font-size:78px;font-weight:900;color:${t.accent};white-space:nowrap}
.stats{display:flex;margin-top:40px;border-top:1px solid ${t.line};padding-top:40px;gap:44px}
.stat{flex:1}
.stat+.stat{border-right:1px solid ${t.line};padding-right:44px}
.num{font-size:${p.stats&&p.stats.length>2?68:62}px;font-weight:900;line-height:1.08;letter-spacing:-.02em;color:${t.accent}}
.lbl{margin-top:14px;font-size:${p.stats&&p.stats.length>2?26:25}px;font-weight:600;color:${t.muted};line-height:1.45}
.rows{margin-top:36px;display:flex;flex-direction:column;gap:16px}
.row{display:grid;grid-template-columns:auto 1fr;gap:6px 22px;align-items:baseline;
  background:${t.panel};border:1px solid ${t.panelBd};border-radius:20px;padding:24px 30px}
.row.hl{border-color:${t.accent};background:${t.chipBg}}
.rk{font-size:34px;font-weight:900;color:${t.fg}}
.rv{font-size:34px;font-weight:900;color:${t.accent};text-align:left}
.rn{grid-column:1/-1;font-size:24px;font-weight:600;color:${t.muted};margin-top:2px}
.list{margin-top:34px;display:flex;flex-direction:column;gap:22px}
.item{display:flex;align-items:flex-start;gap:22px}
.mk{flex:none;width:50px;height:50px;border-radius:15px;background:${t.chipBg};color:${t.accent};
  border:1px solid ${t.chipBd};font-size:26px;font-weight:900;display:flex;align-items:center;
  justify-content:center;line-height:1;margin-top:3px}
.tx{font-size:31px;font-weight:600;line-height:1.52;color:${t.soft};padding-top:6px}
.tx b{color:${t.accent};font-weight:900}
.note{margin-top:38px;font-size:29px;font-weight:700;line-height:1.55;color:${t.fg};
  border-right:4px solid ${t.accent};padding-right:24px}
.src{font-size:19px;font-weight:600;color:${t.muted};margin-top:26px;opacity:.85}
.foot{border-top:1px solid ${t.line};color:${t.muted}}
.foot b{color:${t.accent};font-weight:700}
.wordmark{color:${t.fg}}
${denseCSS}
</style></head><body>
<div class="card"><div class="grain"></div><div class="deco"></div>
  <div class="brand">
    <div class="wordmark"><span class="dot" style="background:${t.accent}"></span>NARA ABROAD</div>
    <div class="tag">${esc(p.tag)}</div>
  </div>
  <div class="body">${blocks.join('')}
    ${p.src?`<div class="src">المصدر: ${p.src}</div>`:''}</div>
  <div class="foot"><span class="ltr">nara-abroad.co.uk</span><span><b class="ltr">@naraabroad_official</b></span></div>
</div></body></html>`;
}

const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args:['--no-sandbox','--font-render-hinting=none'] });
const pg = await b.newPage({ viewport:{width:1080,height:1350}, deviceScaleFactor:1 });
const only = process.argv.slice(2);
for (const p of posts.filter(p => !only.length || only.includes(p.id))) {
  writeFileSync(`gen-${p.id}.html`, render(p));
  await pg.goto(`file://${process.cwd()}/gen-${p.id}.html`);
  await pg.waitForTimeout(450);
  const over = await pg.evaluate(() => {
    const c = document.querySelector('.card');
    return { of: c.scrollHeight - c.clientHeight, bodyH: document.querySelector('.body').scrollHeight };
  });
  await pg.screenshot({ path:`post-${p.id}.jpg`, type:'jpeg', quality:92 });
  console.log(`${p.id}  overflow=${over.of}  bodyH=${over.bodyH}`);
}
await b.close();
