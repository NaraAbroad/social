/* Three additional reels, built from the same design system as the first.
   Each targets a different ad set: parents, students-utility, students-decision. */
import { chromium } from 'playwright';
import { writeFileSync, mkdirSync, rmSync } from 'fs';

const THEMES = {
  navy: { bg:`radial-gradient(900px 900px at 88% -8%, #1D3E70 0%, transparent 60%),
              radial-gradient(820px 820px at 5% 106%, #14305C 0%, transparent 58%),
              linear-gradient(168deg,#0A1A33 0%,#0C2044 55%,#08202E 100%)`,
          fg:'#fff', accent:'#F0B429', soft:'#C6D6EC', muted:'#9FB6D6',
          ring:'rgba(240,180,41,.22)', chip:'rgba(240,180,41,.14)', chipBd:'rgba(240,180,41,.32)',
          panel:'rgba(255,255,255,.05)', panelBd:'rgba(255,255,255,.10)', grain:'rgba(255,255,255,.09)' },
  paper:{ bg:`radial-gradient(900px 900px at 86% 2%, #F3E9D6 0%, transparent 62%),
              radial-gradient(760px 760px at 6% 100%, #EBE0CC 0%, transparent 58%),
              linear-gradient(170deg,#FAF4E8 0%,#F1E7D6 100%)`,
          fg:'#26262A', accent:'#2A5570', soft:'#3A3A36', muted:'#6E6A5F',
          ring:'rgba(42,85,112,.22)', chip:'rgba(42,85,112,.10)', chipBd:'rgba(42,85,112,.30)',
          panel:'rgba(38,38,42,.04)', panelBd:'rgba(38,38,42,.10)', grain:'rgba(38,38,42,.08)' },
  rose: { bg:`radial-gradient(900px 900px at 90% 4%, #F6E2DE 0%, transparent 62%),
              radial-gradient(780px 780px at 4% 102%, #EFE2DC 0%, transparent 58%),
              linear-gradient(172deg,#FBF8F2 0%,#F2E9DF 100%)`,
          fg:'#20222A', accent:'#C0483C', soft:'#33353E', muted:'#6B6A6E',
          ring:'rgba(192,72,60,.24)', chip:'rgba(192,72,60,.10)', chipBd:'rgba(192,72,60,.30)',
          panel:'rgba(32,34,42,.04)', panelBd:'rgba(32,34,42,.10)', grain:'rgba(32,34,42,.08)' },
};

export const REELS = [
  { id:'parents', theme:'navy', dur:24,
    beats:[
      [0.30, 4.20, `<div class="big">ابنك بدّه<br><em>يسافر يدرس.</em></div>`, -120],
      [1.90, 4.20, `<div class="sub">وإنت اللي رح تدفع… وإنت اللي رح تقلق.</div>`, 300],
      [4.60, 9.60, `<div class="mid">قبل ما تقول آه…</div>`, -430],
      [5.60, 9.60, `<div class="row"><div class="mk">؟</div><div class="rt">الجامعة معترف فيها؟</div></div>`, -100],
      [6.80, 9.60, `<div class="row"><div class="mk">؟</div><div class="rt">التكلفة الحقيقية قدّيش؟</div></div>`, 80],
      [8.00, 9.60, `<div class="row"><div class="mk">؟</div><div class="rt">مين بيراجع أوراقه؟</div></div>`, 260],
      [10.00, 13.40, `<div class="big" style="text-align:center">وإذا انرفض<br><em>الطلب؟</em></div>`],
      [13.90, 20.60, `<div class="mid">هاي أسئلة إلها<br><em>أجوبة واضحة.</em></div>`, -400],
      [15.30, 20.60, `<div class="row"><div class="mk ok">✓</div><div class="rt">كل الأرقام قدامك — مش من وسيط</div></div>`, -80],
      [16.90, 20.60, `<div class="row"><div class="mk ok">✓</div><div class="rt">مختص قبول بيراجع كل ورقة</div></div>`, 110],
      [18.50, 20.60, `<div class="row"><div class="mk ok">✓</div><div class="rt">وبنكمّل معه: تأشيرة وسكن وسفر</div></div>`, 300],
      [21.00, 24.0, `<div class="cta">شوفها بعينك.</div><div class="ctas">nara-abroad.co.uk</div>`],
    ]},

  { id:'rejection', theme:'rose', dur:22,
    beats:[
      [0.30, 3.80, `<div class="big">طلبك بينرفض<br><em>قبل ما ينقرا.</em></div>`],
      [2.00, 3.80, `<div class="sub">مش لأنك مش مؤهل.</div>`, 320],
      [4.20, 15.80, `<div class="mid">٥ أسباب بتتكرر:</div>`, -470],
      [5.10, 15.80, `<div class="row"><div class="mk">١</div><div class="rt">ورقة ناقصة أو خانة فاضية</div></div>`, -230],
      [7.00, 15.80, `<div class="row"><div class="mk">٢</div><div class="rt">شرط دقيق ما تحقق — معدل أو مادة</div></div>`, -60],
      [8.90, 15.80, `<div class="row"><div class="mk">٣</div><div class="rt">خلفيتك بعيدة عن التخصص</div></div>`, 110],
      [10.80, 15.80, `<div class="row"><div class="mk">٤</div><div class="rt">إثبات مالي مش بالشكل المطلوب</div></div>`, 280],
      [12.70, 15.80, `<div class="row"><div class="mk">٥</div><div class="rt">تأخرت على الموعد</div></div>`, 450],
      [16.30, 19.20, `<div class="big" style="text-align:center">كلها بتنحل<br><em>بمراجعة وحدة.</em></div>`],
      [19.60, 22.0, `<div class="cta">قبل ما تبعت.</div><div class="ctas">nara-abroad.co.uk</div>`],
    ]},

  { id:'compare', theme:'paper', dur:20,
    beats:[
      [0.30, 3.60, `<div class="big">نفس التخصص.<br><em>تكلفة بتفرق كتير.</em></div>`],
      [4.00, 8.60, `<div class="mid">بين دولة ودولة…</div>`, -400],
      [5.00, 8.60, `<div class="row"><div class="mk">→</div><div class="rt">وبين جامعة وجامعة بنفس الدولة</div></div>`, -140],
      [6.40, 8.60, `<div class="row"><div class="mk">→</div><div class="rt">وبين مدينة ومدينة بنفس الجامعة</div></div>`, 60],
      [9.10, 12.60, `<div class="big" style="text-align:center">الفرق بيغيّر<br><em>قرارك كليًا.</em></div>`],
      [13.10, 17.20, `<div class="mid">بلاش تخمين.</div>`, -300],
      [14.10, 17.20, `<div class="row"><div class="mk ok">✓</div><div class="rt">شوف الأرقام الحقيقية جنب بعض</div></div>`, -40],
      [15.50, 17.20, `<div class="row"><div class="mk ok">✓</div><div class="rt">وقارن قبل ما تقرر</div></div>`, 140],
      [17.70, 20.0, `<div class="cta">قارن بنفسك.</div><div class="ctas">nara-abroad.co.uk</div>`],
    ]},
];

function page(r) {
  const t = THEMES[r.theme];
  return `<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
@font-face{font-family:Cairo;src:url(fonts/cairo-400.ttf);font-weight:400}
@font-face{font-family:Cairo;src:url(fonts/cairo-700.ttf);font-weight:700}
@font-face{font-family:Cairo;src:url(fonts/cairo-900.ttf);font-weight:900}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#0A1A33}
body{font-family:Cairo,sans-serif;-webkit-font-smoothing:antialiased}
#stage{position:relative;width:1080px;height:1920px;overflow:hidden;background:${t.bg};color:${t.fg}}
.grain{position:absolute;inset:0;opacity:.55;background-size:30px 30px;
  background-image:radial-gradient(circle at 1px 1px, ${t.grain} 1px, transparent 0)}
#ring{position:absolute;width:1320px;height:1320px;border-radius:50%;border:2px solid ${t.ring};top:300px;left:-120px}
#bar{position:absolute;top:0;right:0;height:8px;background:${t.accent};z-index:9}
#mark{position:absolute;top:74px;right:72px;display:flex;align-items:center;gap:16px;
  font-weight:700;font-size:30px;letter-spacing:.28em;z-index:8}
#mark i{width:18px;height:18px;border-radius:50%;background:${t.accent};display:block}
#site{position:absolute;bottom:78px;right:0;left:0;text-align:center;color:${t.muted};
  font-size:34px;font-weight:700;direction:ltr;z-index:8}
.beat{position:absolute;right:92px;left:92px;text-align:right;will-change:transform,opacity}
.big{font-size:112px;font-weight:900;line-height:1.34;letter-spacing:-.02em}
.big em{font-style:normal;color:${t.accent}}
.mid{font-size:78px;font-weight:900;line-height:1.36}
.mid em{font-style:normal;color:${t.accent}}
.sub{font-size:50px;font-weight:700;line-height:1.5;color:${t.soft}}
.row{display:flex;align-items:center;gap:28px}
.mk{flex:none;width:86px;height:86px;border-radius:24px;background:${t.chip};border:1px solid ${t.chipBd};
  color:${t.accent};font-size:44px;font-weight:900;display:flex;align-items:center;justify-content:center}
.mk.ok{background:${t.accent};color:${t.theme==='paper'?'#FAF4E8':'#08202E'};border-color:${t.accent}}
.rt{font-size:62px;font-weight:700;line-height:1.4;color:${t.soft}}
.cta{font-size:132px;font-weight:900;color:${t.accent};line-height:1.3;text-align:center}
.ctas{font-size:52px;font-weight:700;text-align:center;margin-top:24px;direction:ltr;color:${t.fg}}
</style></head><body><div id="stage">
<div class="grain"></div><div id="ring"></div>
<div id="mark"><i></i>NARA ABROAD</div><div id="bar"></div>
<div id="site">nara-abroad.co.uk</div><div id="layer"></div></div>
<script>
const DUR=${r.dur};
const B=${JSON.stringify(r.beats)};
const layer=document.getElementById('layer');
const els=B.map(b=>{const d=document.createElement('div');d.className='beat';d.innerHTML=b[2];
  d.style.top=(960+(b[3]||0))+'px';layer.appendChild(d);
  d.style.marginTop=(-d.offsetHeight/2)+'px';return d;});
const ease=p=>1-Math.pow(1-p,3), cl=v=>Math.max(0,Math.min(1,v));
window.render=function(t){
  document.getElementById('bar').style.width=(t/DUR*1080)+'px';
  document.getElementById('ring').style.transform='rotate('+(t*5)+'deg)';
  B.forEach((b,i)=>{const el=els[i],IN=.42,OUT=.30;
    if(t<b[0]-0.02||t>b[1]+OUT){el.style.opacity=0;return;}
    const pin=ease(cl((t-b[0])/IN)), pout=cl((t-b[1])/OUT);
    el.style.opacity=pin*(1-pout);
    el.style.transform='translateY('+((1-pin)*70-pout*45)+'px) scale('+(0.955+0.045*pin)+')';});
};
render(0);
</script></body></html>`;
}

const FPS = 30;
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args:['--no-sandbox','--font-render-hinting=none'] });
const p = await b.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
for (const r of REELS) {
  writeFileSync(`reel-${r.id}.html`, page(r));
  const dir = `frames-${r.id}`;
  rmSync(dir, { recursive:true, force:true }); mkdirSync(dir);
  await p.goto(`file://${process.cwd()}/reel-${r.id}.html`);
  await p.waitForTimeout(800);
  const n = Math.round(r.dur * FPS);
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => window.render(t), i / FPS);
    await p.screenshot({ path:`${dir}/f${String(i).padStart(4,'0')}.jpg`, type:'jpeg', quality:95 });
  }
  console.log(`${r.id}: ${n} frames (${r.dur}s)`);
}
await b.close();
