const fs=require('fs');const html=fs.readFileSync(require('path').join(__dirname,'..','index.html'),'utf8');
const s=html.indexOf('const PROBS=[');let d=0,i=html.indexOf('[',s),e;for(;i<html.length;i++){if(html[i]=='[')d++;else if(html[i]==']'){d--;if(!d){e=i;break;}}}
const src=html.slice(s,e+1);
const pre=`const ri=(a,b)=>a+Math.floor(Math.random()*(b-a+1));const pick=a=>a[Math.floor(Math.random()*a.length)];
const fmt=(v,d=2)=>{if(!isFinite(v))return'—';const a=Math.abs(v);let s=a!==0&&(a<0.01||a>=1e5)?v.toExponential(2):v.toFixed(d);return s.replace('-','−')};
const num=v=>(+v.toFixed(3)).toString();`;
// try to pull real helper defs
const grab=n=>{const m=html.match(new RegExp('(?:const|function) '+n+'\\b[^\\n]*'));return m?m[0]:''};
const L=html.split('\n'),h0=L.findIndex(l=>l.includes('/* ---------------- 07 Practice'));let helpers=L.slice(h0,h0+6).join('\n')+'\nconst G=9.8;'+html.match(/function fmt[^\n]*/)[0]+html.match(/function num[^\n]*/)[0];
eval(helpers+'\n'+src.replace('const PROBS','globalThis.PROBS'));
const strip=h=>h.replace(/<[^>]+>/g,'').replace(/&nbsp;/g,' ').replace(/\s+/g,' ');
for(const p of PROBS){const g=p.gen();console.log(`### ${p.id} [${p.topic}] ${p.title}\nQ: ${strip(g.q)}\nANS: ${g.ans} ${g.unit||''}\nSOL: ${strip(g.sol)}\n`);}
