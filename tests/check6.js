const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
(async()=>{const b=await chromium.launch();
for (const [w,dark] of [[1280,false],[400,true]]){
const p=await b.newPage({viewport:{width:w,height:900},colorScheme:dark?'dark':'light'});
p.on('pageerror',e=>console.log('PAGEERR',w,e.message));p.on('console',m=>{if(m.type()==='error')console.log('ERR',m.text())});
await p.goto('file://'+require('path').resolve(process.argv[2]||require('path').join(__dirname,'..','index.html')));
if(w===1280){const d=await p.evaluate(()=>{const ids={};document.querySelectorAll('[id]').forEach(e=>ids[e.id]=(ids[e.id]||0)+1);return Object.entries(ids).filter(([k,v])=>v>1)});console.log('dup ids',JSON.stringify(d));
 console.log('groups',await p.evaluate(()=>Array.from(document.querySelectorAll('#nav .grp')).map(g=>{let n=0,e=g.nextElementSibling;while(e&&e.tagName==='A'){n++;e=e.nextElementSibling}return g.textContent+':'+n}).join(' | ')));}
const views=await p.evaluate(()=>['overview',...Array.from(document.querySelectorAll('#nav a')).map(a=>a.dataset.view)].filter((v,i,a)=>a.indexOf(v)===i));
for(const v of views){await p.evaluate(v=>location.hash=v,v);await p.waitForTimeout(300);
  if(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth))console.log('OVERFLOW',w,v);
  const blank=await p.evaluate(()=>Array.from(document.querySelectorAll('.view:not([hidden]) canvas')).filter(c=>{if(!c.width||!c.clientWidth)return true;const x=c.getContext('2d').getImageData(0,0,c.width,c.height).data;for(let i=3;i<x.length;i+=40)if(x[i])return false;return true}).map(c=>c.id));
  if(blank.length)console.log('BLANK',w,v,blank);
  const bad=await p.evaluate(()=>(document.querySelector('.view:not([hidden])').innerText.match(/NaN|undefined|Infinity/g)||[]).length);if(bad)console.log('BADTEXT',v);
  if(w===1280){const n=await p.evaluate(()=>document.querySelectorAll('.view:not([hidden]) [data-show]').length);
    for(let i=0;i<n;i++){await p.evaluate(i=>document.querySelectorAll('.view:not([hidden]) [data-show]')[i].click(),i);await p.waitForTimeout(120);
      const bad2=await p.evaluate(()=>(document.querySelector('.view:not([hidden])').innerText.match(/NaN|undefined/g)||[]).length);if(bad2)console.log('SHOWBAD',v,i);}}
}
if(w===1280){for(const v of ['torque','impulse','pulleys','beats']){await p.evaluate(v=>location.hash=v,v);await p.waitForTimeout(400);await p.evaluate(()=>document.querySelector('.view:not([hidden]) .lab').scrollIntoView());await p.waitForTimeout(600);await p.screenshot({path:'r-'+`${v}.png`});}
 await p.evaluate(()=>location.hash='overview');await p.waitForTimeout(300);await p.evaluate(()=>document.querySelector('#modgrid').scrollIntoView());await p.screenshot({path:'r-over.png'});}
await p.close();}
await b.close();})();
