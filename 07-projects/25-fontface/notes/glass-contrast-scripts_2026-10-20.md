# Glass contrast scripts (2026-10-20)

These scripts back the transparency numbers in [unicron-migration-plan_2026-10-20.md](unicron-migration-plan_2026-10-20.md) §5 (contrast) and [window-translucency-learnings_2026-10-20.md](window-translucency-learnings_2026-10-20.md).
They were first written in a session scratchpad, which is temporary, so they are kept here.

**What they do.**
Each one mixes a see-through surface colour over a worst-case backdrop.
It then measures text contrast with APCA (the Accessible Perceptual Contrast Algorithm, the WCAG 3 draft method) and, in `solve.mjs`, the WCAG 2 ratio too.
The goal is the weakest surface opacity (alpha) that keeps muted text at or above APCA Lc 75.

**Worst-case backdrops used.**
- Light mode, blurred look: grey `#999999`. Plain look: black.
- Dark mode, blurred look: grey `#737373`. Plain look: white.

**How to run.**
They need the `apca-w3` package.
The import path points at Synapse's copy (`/Users/sean.sands/Projects/synapse/app/node_modules/apca-w3`).
If that moves, run `npm i apca-w3` in a scratch folder and change the import.
Run each with `node <file>.mjs`.

| Script | Answers |
|---|---|
| `calib.mjs` | Minimum sidebar alpha on Unicron's ramp, for several grey backdrops, with and without a 7% selected row. |
| `menu.mjs` | Whether a 70% popover menu stays readable over a solid sidebar, a glass sidebar, and opposite-polarity content. |
| `solve.mjs` | (A) Fontface's shipped tints. (B) Unicron's solid baseline and the weakest glass alpha per role. (C) Fontface's alphas on Unicron's colours. |
| `solve2.mjs` | Solid selected-row contrast, the minimum sidebar alpha, and the muted-text lightness needed at alphas 0.5–0.8. |

## calib.mjs

```js
import { APCAcontrast, sRGBtoY } from "/Users/sean.sands/Projects/synapse/app/node_modules/apca-w3/src/apca-w3.js";
const deg=Math.PI/180, gamma=c=>c<=0.0031308?12.92*c:1.055*c**(1/2.4)-0.055;
function oklch(L,C=0,h=0){const a=C*Math.cos(h*deg),b=C*Math.sin(h*deg);const l_=L+0.3963377774*a+0.2158037573*b,m_=L-0.1055613458*a-0.0638541728*b,s_=L-0.0894841775*a-1.291485548*b;const l=l_**3,m=m_**3,s=s_**3;return [4.0767416621*l-3.3077115913*m+0.2309699292*s,-1.2684380046*l+2.6097574011*m-0.3413193965*s,-0.0041960863*l-0.7034186147*m+1.707614701*s].map(c=>gamma(Math.min(1,Math.max(0,c)))*255);}
const over=(fg,a,bg)=>fg.map((c,i)=>c*a+bg[i]*(1-a)), r8=x=>x.map(Math.round);
const lc=(t,b)=>Math.abs(APCAcontrast(sRGBtoY(r8(t)),sRGBtoY(r8(b))));
const n=(L,C)=>oklch(L,C,260);
const light={sb:n(.974,.003),fg:n(.145,.006),muted:n(.44,.012)};
const dark={sb:n(.185,.008),fg:n(.987,.002),muted:n(.91,.006)};
const solve=(u,back,sel)=>{for(let a=0;a<=1.00001;a+=0.01){const s=over(u.sb,a,back);const r=over(u.fg,0.07,s);if(lc(u.muted,s)>=75&&lc(u.fg,s)>=75&&(!sel||lc(u.muted,r)>=75))return a.toFixed(2)}return "none"};
console.log("light chrome: worst backdrop -> min alpha (sidebar only / with 7% selected row)");
for (const h of [0x99,0xb3,0xcc,0xe0]) { const b=[h,h,h]; console.log(`#${h.toString(16).repeat(3)}: ${solve(light,b,false)} / ${solve(light,b,true)}`); }
console.log("dark chrome:");
for (const h of [0x73,0x5a,0x40,0x26]) { const b=[h,h,h]; console.log(`#${h.toString(16).padStart(2,"0").repeat(3)}: ${solve(dark,b,false)} / ${solve(dark,b,true)}`); }
```

## menu.mjs

```js
import { APCAcontrast, sRGBtoY } from "/Users/sean.sands/Projects/synapse/app/node_modules/apca-w3/src/apca-w3.js";
const deg=Math.PI/180, gamma=c=>c<=0.0031308?12.92*c:1.055*c**(1/2.4)-0.055;
function oklch(L,C=0,h=0){const a=C*Math.cos(h*deg),b=C*Math.sin(h*deg);const l_=L+0.3963377774*a+0.2158037573*b,m_=L-0.1055613458*a-0.0638541728*b,s_=L-0.0894841775*a-1.291485548*b;const l=l_**3,m=m_**3,s=s_**3;return [4.0767416621*l-3.3077115913*m+0.2309699292*s,-1.2684380046*l+2.6097574011*m-0.3413193965*s,-0.0041960863*l-0.7034186147*m+1.707614701*s].map(c=>gamma(Math.min(1,Math.max(0,c)))*255);}
const over=(fg,a,bg)=>fg.map((c,i)=>c*a+bg[i]*(1-a)), r8=x=>x.map(Math.round);
const lc=(t,b)=>Math.abs(APCAcontrast(sRGBtoY(r8(t)),sRGBtoY(r8(b))));
const gray=v=>[v*255,v*255,v*255];
const n=(L,C)=>oklch(L,C,260);
// Menu bg-popover/70 over: (a) solid sidebar (today), (b) sidebar glass 0.45 light / 0.60 dark over worst blur backdrop, (c) bare worst backdrop (body transparent)
const M={light:{pop:n(1,0),fg:n(.145,.006),muted:n(.44,.012),sb:n(.974,.003),back:gray(0x99/255),a:.45, worstPage:gray(0)},dark:{pop:n(.185,.008),fg:n(.987,.002),muted:n(.91,.006),sb:n(.185,.008),back:gray(0x73/255),a:.60, worstPage:gray(1)}};
for (const m of ["light","dark"]) { const u=M[m];
  const today=over(u.pop,.7,u.sb), glass=over(u.pop,.7,over(u.sb,u.a,u.back));
  // worst in-page content under a menu: text of opposite polarity (a black word under a light menu) — blur averages it, but a large dark image can approach this
  const worstContent=over(u.pop,.7,u.worstPage);
  console.log(`${m}: menu over solid sidebar muted Lc ${lc(u.muted,today).toFixed(1)} fg ${lc(u.fg,today).toFixed(1)} | over glass sidebar muted ${lc(u.muted,glass).toFixed(1)} fg ${lc(u.fg,glass).toFixed(1)} | over opposite-polarity content muted ${lc(u.muted,worstContent).toFixed(1)} fg ${lc(u.fg,worstContent).toFixed(1)}`);
}
```

## solve.mjs

```js
import { APCAcontrast, sRGBtoY } from "/Users/sean.sands/Projects/synapse/app/node_modules/apca-w3/src/apca-w3.js";
const deg = Math.PI/180;
const gamma = c => c <= 0.0031308 ? 12.92*c : 1.055*c**(1/2.4)-0.055;
const lin = c => c <= 0.04045 ? c/12.92 : ((c+0.055)/1.055)**2.4;
function oklch(L,C=0,h=0){ const a=C*Math.cos(h*deg), b=C*Math.sin(h*deg);
  const l_=L+0.3963377774*a+0.2158037573*b, m_=L-0.1055613458*a-0.0638541728*b, s_=L-0.0894841775*a-1.291485548*b;
  const l=l_**3,m=m_**3,s=s_**3;
  return [4.0767416621*l-3.3077115913*m+0.2309699292*s, -1.2684380046*l+2.6097574011*m-0.3413193965*s, -0.0041960863*l-0.7034186147*m+1.707614701*s].map(c=>gamma(Math.min(1,Math.max(0,c)))*255);
}
const over=(fg,a,bg)=>fg.map((c,i)=>c*a+bg[i]*(1-a));
const r8=x=>x.map(Math.round);
const lc=(t,b)=>Math.abs(APCAcontrast(sRGBtoY(r8(t)),sRGBtoY(r8(b))));
const wl=x=>{const [r,g,b]=x.map(c=>lin(c/255));return .2126*r+.7152*g+.0722*b};
const wr=(a,b)=>{const [h,l]=[wl(a),wl(b)].sort((x,y)=>y-x);return (h+.05)/(l+.05)};
const gray=v=>[v*255,v*255,v*255];
const BACK={light:{blur:gray(0x99/255),plain:gray(0)},dark:{blur:gray(0x73/255),plain:gray(1)}};
const f=(x)=>x.toFixed(1);

// A) Fontface as shipped (achromatic greys)
const FF={light:{sb:[oklch(.985),.45],sbp:[oklch(.985),.88],acc:[oklch(.145),.07],pane:[oklch(1),.92],panep:[oklch(1),.97],faint:oklch(.4),faintPane:oklch(.53),main:oklch(.145),sbText:oklch(.145)},
 dark:{sb:[oklch(.205),.60],sbp:[oklch(.205),.90],acc:[oklch(.985),.07],pane:[oklch(.145),.92],panep:[oklch(.145),.96],faint:oklch(.8),faintPane:oklch(.708),main:oklch(.985),sbText:oklch(.985)}};
console.log("A) Fontface tints, worst-case backdrop: WCAG ratio / APCA Lc");
for (const m of ["light","dark"]) for (const look of ["blur","plain"]) {
  const t=FF[m], back=BACK[m][look];
  const sb = look==="blur"? over(...t.sb,back) : over(...t.sbp,back);
  const sel = over(t.acc[0],t.acc[1],sb);
  const pane = look==="blur"? over(...t.pane,back): over(...t.panep,back);
  console.log(`${m}/${look}: faint on sidebar ${f(wr(t.faint,sb))}:1 Lc ${f(lc(t.faint,sb))} | faint on selected ${f(wr(t.faint,sel))}:1 Lc ${f(lc(t.faint,sel))} | faint on pane ${f(wr(t.faintPane,pane))}:1 Lc ${f(lc(t.faintPane,pane))} | main on pane ${f(wr(t.main,pane))}:1 Lc ${f(lc(t.main,pane))} | sidebar text Lc ${f(lc(t.sbText,sb))}`);
}

// B) Unicron ramp (hue 260). Solve the weakest alpha for each glass role so muted-foreground clears Lc 75.
const N = { "0":[1,0,260],"25":[.987,.002,260],"50":[.974,.003,260],"100":[.948,.004,260],"200":[.91,.006,260],"600":[.44,.012,260],"800":[.26,.01,260],"900":[.185,.008,260],"950":[.145,.006,260] };
const n=k=>oklch(...N[k]);
const U={light:{sidebar:n("50"),bg:n("0"),muted:n("600"),fg:n("950"),accFg:n("950")},dark:{sidebar:n("900"),bg:n("950"),muted:n("200"),fg:n("25"),accFg:n("25")}};
console.log("\nB) Unicron solid baseline: muted on sidebar / background (Lc)");
for (const m of ["light","dark"]) console.log(m, f(lc(U[m].muted,U[m].sidebar)), f(lc(U[m].muted,U[m].bg)));
console.log("\nB) Unicron ramp: weakest alpha that keeps muted-foreground >= Lc 75 (and selected row = foreground/7% over it)");
for (const m of ["light","dark"]) for (const look of ["blur","plain"]) {
  const back=BACK[m][look]; const u=U[m];
  const solve=(surface,withSel)=>{ for(let a=0.30;a<=1.0001;a+=0.01){ const s=over(surface,a,back); const sel=over(u.fg,0.07,s); const ok = lc(u.muted,s)>=75 && (!withSel || lc(u.muted,sel)>=75); if(ok) return a; } return null; };
  const aS=solve(u.sidebar,true), aP=solve(u.bg,false);
  console.log(`${m}/${look}: sidebar glass >= ${aS?.toFixed(2)} | content glass >= ${aP?.toFixed(2)}`);
}
// C) With Fontface's glass alphas on Unicron's ramp, what does muted get?
console.log("\nC) Fontface alphas on Unicron colours, muted-foreground Lc (sidebar / selected / pane)");
const AL={light:{blur:[.45,.92],plain:[.88,.97]},dark:{blur:[.60,.92],plain:[.90,.96]}};
for (const m of ["light","dark"]) for (const look of ["blur","plain"]) {
  const back=BACK[m][look]; const u=U[m]; const [as,ap]=AL[m][look];
  const s=over(u.sidebar,as,back), sel=over(u.fg,.07,s), p=over(u.bg,ap,back);
  console.log(`${m}/${look}: ${f(lc(u.muted,s))} / ${f(lc(u.muted,sel))} / ${f(lc(u.muted,p))}   (foreground on sidebar ${f(lc(u.fg,s))})`);
}
```

## solve2.mjs

```js
import { APCAcontrast, sRGBtoY } from "/Users/sean.sands/Projects/synapse/app/node_modules/apca-w3/src/apca-w3.js";
const deg=Math.PI/180, gamma=c=>c<=0.0031308?12.92*c:1.055*c**(1/2.4)-0.055;
function oklch(L,C=0,h=0){const a=C*Math.cos(h*deg),b=C*Math.sin(h*deg);const l_=L+0.3963377774*a+0.2158037573*b,m_=L-0.1055613458*a-0.0638541728*b,s_=L-0.0894841775*a-1.291485548*b;const l=l_**3,m=m_**3,s=s_**3;return [4.0767416621*l-3.3077115913*m+0.2309699292*s,-1.2684380046*l+2.6097574011*m-0.3413193965*s,-0.0041960863*l-0.7034186147*m+1.707614701*s].map(c=>gamma(Math.min(1,Math.max(0,c)))*255);}
const over=(fg,a,bg)=>fg.map((c,i)=>c*a+bg[i]*(1-a)), r8=x=>x.map(Math.round);
const lc=(t,b)=>Math.abs(APCAcontrast(sRGBtoY(r8(t)),sRGBtoY(r8(b))));
const gray=v=>[v*255,v*255,v*255];
const BACK={light:{blur:gray(0x99/255),plain:gray(0)},dark:{blur:gray(0x73/255),plain:gray(1)}};
const n=(L,C)=>oklch(L,C,260);
const U={light:{sidebar:n(.974,.003),bg:n(1,0),fg:n(.145,.006),muted:n(.44,.012),acc:n(.948,.004)},dark:{sidebar:n(.185,.008),bg:n(.145,.006),fg:n(.987,.002),muted:n(.91,.006),acc:n(.26,.01)}};
console.log("solid selected row (sidebar-accent) muted Lc:", ["light","dark"].map(m=>lc(U[m].muted,U[m].acc).toFixed(1)));
for (const m of ["light","dark"]) for (const look of ["blur","plain"]) {
  const back=BACK[m][look], u=U[m];
  let line=`${m}/${look}:`;
  // min alpha for sidebar alone: muted >= 75 and fg >= 75
  let aMin=null; for(let a=0.3;a<=1.00001;a+=0.01){const s=over(u.sidebar,a,back); if(lc(u.muted,s)>=75&&lc(u.fg,s)>=75){aMin=a;break}}
  line+=` sidebar alone >= ${aMin?.toFixed(2)};`;
  // for alphas, the muted L (glass muted) needed on sidebar and selected row (fg 7%)
  for (const a of [0.5,0.6,0.7,0.8]) {
    const s=over(u.sidebar,a,back), sel=over(u.fg,0.07,s);
    let need=null;
    const Ls = m==="light"? [...Array(45)].map((_,i)=>0.44-i*0.01) : [...Array(10)].map((_,i)=>0.91+i*0.01);
    for (const L of Ls){ const t=n(L,.012); if(lc(t,s)>=75&&lc(t,sel)>=75){need=L;break} }
    line+=` a=${a}: fg ${lc(u.fg,s).toFixed(0)}, glass-muted L ${need===null?"none":need.toFixed(2)};`;
  }
  console.log(line);
}
```
