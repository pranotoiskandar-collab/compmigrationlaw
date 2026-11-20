const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.cwd()+'/report-id.html',{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
await p.pdf({path:'imr-laporan-tahunan-2026.pdf',format:'A4',printBackground:true,preferCSSPageSize:true});
await p.setViewportSize({width:794,height:1123});
const n=await p.$$eval('.page',a=>a.length);
for(let i=0;i<n;i++){const el=(await p.$$('.page'))[i];await el.screenshot({path:`id-pg${i+1}.png`});}
const over=await p.$$eval('.page',a=>a.map((e,i)=>{const r=e.getBoundingClientRect();let m=0;e.querySelectorAll('*:not(.art):not(.art *)').forEach(c=>{const b=c.getBoundingClientRect();if(b.bottom>m&&!c.closest('.foot'))m=b.bottom});return [i+1,Math.round(r.bottom-m)]}));
console.log(n,JSON.stringify(over));await b.close();})();
