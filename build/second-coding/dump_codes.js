const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();const out={};
for(const [k,u,v] of [['ea','/east-asia/','EA'],['sea','/southeast-asia/','SEA'],['oc','/countries-of-origin/','OC']]){await p.goto('http://localhost:8765'+u);await p.waitForTimeout(1500);
out[k]=await p.evaluate(v=>{const G=window[v];return {codebook:G.codebook,states:G.states,groups:G.groups?G.groups.map(g=>({k:g.k,n:g.n,s:g.s,codes:g.codes})):null,codes:G.codes||null,laws:G.laws}},v);}
require('fs').writeFileSync('codes.json',JSON.stringify(out));
console.log(JSON.stringify(out.oc.codebook[0]).slice(0,400));console.log(JSON.stringify(out.ea.groups[0]).slice(0,500));console.log(JSON.stringify(out.oc.states).slice(0,300));console.log(JSON.stringify(out.ea.laws[0]));await b.close();})();
