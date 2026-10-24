#!/usr/bin/env python3
"""Build both Mechanics sites from one source.

    python3 build.py                      # Intulab version  -> index.html
    python3 build.py --phy ../phy103-lab  # Princeton Labs PHY 103 version -> ../phy103-lab/index.html
    python3 build.py --all ../phy103-lab  # both

src/site.html is the shared page: every module, simulation, worked example, quiz and problem.
This script turns it into two sites by exact text edits:

  AP version (Mechanics Lab, part of Intulab)
    modules grouped by AP Physics C units, damping and waves under "Beyond AP C",
    AP countdown, formula sheet, FRQ practice, exam format box, GoatCounter visit counts,
    College Board legal text, reports to jiacode2030/intulab-feedback.

  PHY 103 version (PHY 103 Lab, part of Princeton Labs)
    modules grouped by PHY 103 weeks, no AP content (no countdown, FRQ, exam format box),
    a Key formulas page instead of the formula drawer, no analytics,
    Princeton legal text, reports to jiacode2030/phy103-lab, its own progress keys (phy-).

Every edit must find its text exactly (most exactly once), or the build stops. So if you change
src/site.html and an edit no longer matches, you get an error instead of a half-converted site.
After building, both outputs are scanned for words that belong to the other site.
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src', 'site.html')


class Page:
    def __init__(self, text, name):
        self.s, self.name = text, name

    def rep(self, old, new, count=1):
        n = self.s.count(old)
        if (count == 'all' and n == 0) or (count != 'all' and n != count):
            sys.exit(f'[{self.name}] expected {count} of: {old[:90]!r} (found {n})')
        self.s = self.s.replace(old, new)

    def cut(self, start, end, include_end=True, new=''):
        """Replace from `start` through `end` (the first `end` after `start`)."""
        i = self.s.find(start)
        if i < 0 or self.s.count(start) != 1:
            sys.exit(f'[{self.name}] cut start not unique: {start[:80]!r}')
        j = self.s.find(end, i + len(start))
        if j < 0:
            sys.exit(f'[{self.name}] cut end not found: {end[:80]!r}')
        j += len(end) if include_end else 0
        removed = self.s[i:j]
        self.s = self.s[:i] + new + self.s[j:]
        return removed


def shared_edits(p):
    """Same for both: the course table on the overview is generated from GROUPS."""
    p.cut('<div class="tablewrap">\n        <table>\n          <thead><tr><th>Week</th>', '</table>\n      </div>',
          new='<div class="tablewrap">\n        <table>\n          <thead><tr><th id="map-col">Week</th><th>Topic</th><th>Modules</th></tr></thead>\n'
              '          <tbody id="map-body"></tbody>\n        </table>\n      </div>')
    p.rep("$('#nav').innerHTML=nh;",
          "$('#nav').innerHTML=nh;{const mb=$('#map-body');if(mb)mb.innerHTML=GROUPS.map(g=>`<tr><td>${g.w}</td><td>${g.name}</td><td>${g.ids.map(id=>`<a href=\"#${id}\">${MODS[id].t}</a>`).join(', ')}</td></tr>`).join('');}")


APP_HEAD = '<link rel="manifest" href="/intulab/manifest.webmanifest">\n<meta name="theme-color" content="#0A1220">\n<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-title" content="Intulab">\n<meta name="apple-mobile-web-app-status-bar-style" content="default">\n<link rel="apple-touch-icon" href="/intulab/icons/apple-touch-icon.png">\n'
OG_HEAD = r'''<meta property="og:type" content="website">
<meta property="og:site_name" content="Intulab">
<meta property="og:title" content="Mechanics Lab · Intulab">
<meta property="og:description" content="Live simulations, worked examples and randomized practice for AP Physics C: Mechanics. Free, no sign-up.">
<meta property="og:url" content="https://jiacode2030.github.io/physics-mechanics/">
<meta property="og:image" content="https://jiacode2030.github.io/physics-mechanics/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Mechanics Lab, part of Intulab">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Mechanics Lab · Intulab">
<meta name="twitter:description" content="Live simulations, worked examples and randomized practice for AP Physics C: Mechanics. Free, no sign-up.">
<meta name="twitter:image" content="https://jiacode2030.github.io/physics-mechanics/og.png">
<meta name="description" content="Live simulations, worked examples and randomized practice for AP Physics C: Mechanics. Free, no sign-up.">
'''
APP_HEAD += OG_HEAD
APP_REG = "/* Intulab app: offline support (sw.js). Only on the live site, and localhost for testing. */\nif('serviceWorker' in navigator&&(/\\.github\\.io$/.test(location.hostname)||location.hostname==='localhost'))addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));\n"

# "Get the app" button and steps dialog (AP version only)
APP_BTN = '<button type="button" class="morelabs appbtn" id="app-btn" hidden aria-haspopup="dialog" aria-label="Get the Intulab app"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M12 7v7M9 11l3 3 3-3"/></svg><span class="tl">Get the app</span></button>'
APP_DLG = '<dialog class="appdlg" id="app-dlg" aria-labelledby="app-dlg-h">\n  <form method="dialog">\n    <h2 id="app-dlg-h">Get the Intulab app</h2>\n    <p>Mechanics, E&amp;M, Chemistry, Calculus and Biology in one free app, with no app store. It opens full screen from your home screen, and once you\'ve opened it, it works offline too.</p>\n    <div class="appos" data-os="ios"><h3>iPhone or iPad (Safari)</h3><ol><li>Tap the <b>Share</b> button at the bottom (or top) of Safari.</li><li>Scroll down and tap <b>Add to Home Screen</b>.</li><li>Tap <b>Add</b>.</li></ol>\n      <p class="appnote">On iPhone and iPad, the app keeps its own saved progress, separate from Safari.</p></div>\n    <div class="appos" data-os="android"><h3>Android (Chrome)</h3><ol><li>Tap the <b>⋮</b> menu at the top right.</li><li>Tap <b>Install app</b> (or <b>Add to Home screen</b>).</li><li>Tap <b>Install</b>.</li></ol></div>\n    <div class="appos" data-os="desktop"><h3>Computer (Chrome or Edge)</h3><ol><li>Click the install icon at the right end of the address bar.</li><li>Click <b>Install</b>.</li></ol></div>\n    <div class="approw"><button class="btn primary" value="close">Got it</button></div>\n  </form>\n</dialog>\n'
APP_CSS = "\n/* Get the Intulab app: button in the rail and the steps dialog */\n.appbtn,.appbtn2{cursor:pointer}\n.appbtn[hidden],.appbtn2[hidden]{display:none!important}\n/* computers: in the side rail; phones: on the course's home page (the top bar is full) */\n@media (max-width:900px){.appbtn{display:none!important}}\n@media (min-width:901px){.appbtn2{display:none!important}}\n.appdlg{max-width:min(520px,calc(100vw - 32px));max-height:calc(100dvh - 32px);overflow:auto;width:100%;border:1px solid var(--line);border-radius:16px;background:var(--surface);color:var(--ink);padding:22px;box-shadow:0 20px 50px rgba(0,0,0,.35)}\n.appdlg::backdrop{background:rgba(5,10,20,.55)}\n.appdlg h2{margin:0 0 8px;font-size:22px}\n.appdlg h3{margin:16px 0 6px;font-size:15px}\n.appdlg p{margin:0 0 4px;color:var(--muted)}\n.appdlg ol{margin:0;padding-left:22px}.appdlg li{margin:4px 0}\n.appdlg .appnote{font-size:13.5px;margin-top:8px}\n.appdlg details{margin-top:14px;border-top:1px solid var(--line);padding-top:6px}\n.appdlg summary{cursor:pointer;min-height:44px;display:flex;align-items:center;font-weight:600}\n.appdlg summary::before{content:'▸';margin-right:8px}.appdlg details[open] summary::before{content:'▾'}\n.appdlg .approw{display:flex;justify-content:flex-end;margin-top:18px}\n"
APP_JS = '/* Get the Intulab app (same app as the Intulab page; hidden once you\'re in it) */\n(function appInstall(){var btns=document.querySelectorAll(\'.appbtn,.appbtn2\'),dlg=document.getElementById(\'app-dlg\');if(!btns.length||!dlg)return;\n  var each=function(f){Array.prototype.forEach.call(btns,f);};\n  if(matchMedia(\'(display-mode: standalone)\').matches||navigator.standalone===true)return;\n  each(function(b){b.hidden=false;});var prompt=null;\n  var ua=navigator.userAgent,os=/iPhone|iPad|iPod/.test(ua)||(/Macintosh/.test(ua)&&navigator.maxTouchPoints>1)?\'ios\':/Android/.test(ua)?\'android\':\'desktop\';\n  var form=dlg.querySelector(\'form\'),mine=dlg.querySelector(\'[data-os="\'+os+\'"]\'),more=document.createElement(\'details\');more.innerHTML=\'<summary>Other devices</summary>\';\n  Array.prototype.forEach.call(dlg.querySelectorAll(\'.appos\'),function(el){if(el!==mine)more.appendChild(el);});form.insertBefore(more,form.querySelector(\'.approw\'));\n  addEventListener(\'beforeinstallprompt\',function(e){e.preventDefault();prompt=e;});\n  addEventListener(\'appinstalled\',function(){each(function(b){b.hidden=true;});});\n  each(function(b){b.addEventListener(\'click\',function(){if(prompt){prompt.prompt();prompt=null;return;}if(dlg.showModal)dlg.showModal();else dlg.setAttribute(\'open\',\'\');});});})();\n'
APPEAL_CSS = r'''/* ===== Module appeal layer: the Precalculus Lab look (soft tinted cards, rounded shapes, accent glow on the active tab) in this site's own colors ===== */
:root{--m-acc:var(--accent);--m-on:#FFFFFF;--m-r:16px;--m-acc-d:color-mix(in srgb,var(--m-acc) 78%,#000);--m-lav:#8B7CFF}
:root[data-theme="dark"]{--m-on:#06101F;--m-acc-d:color-mix(in srgb,var(--m-acc) 72%,#fff)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--m-on:#06101F;--m-acc-d:color-mix(in srgb,var(--m-acc) 72%,#fff)}}
.rail{background:linear-gradient(180deg,color-mix(in srgb,var(--m-acc) 9%,var(--surface)),var(--surface) 45%)}
.nav a{border-radius:12px;transition:background .18s,color .18s,transform .18s}
.nav a:hover{background:color-mix(in srgb,var(--m-acc) 12%,transparent);transform:translateX(2px)}
.nav a[aria-current="page"],.nav .ind,.steps .ind,.steps a.on{box-shadow:0 4px 12px color-mix(in srgb,var(--m-acc) 35%,transparent)}
.nav .grp{color:var(--m-acc-d)}
.searchbtn,.themebtn,.btn,.seg,select,input[type=text]{border-radius:12px}
.btn:hover{background:color-mix(in srgb,var(--m-acc) 10%,var(--surface));border-color:color-mix(in srgb,var(--m-acc) 45%,var(--line))}
.btn.primary{box-shadow:0 6px 16px color-mix(in srgb,var(--m-acc) 30%,transparent)}
.steps a{border-radius:999px}
.lab,.example,.sorter,.frq,.prob,.strobe,.start>div,.mod,.tablewrap,.hs-row,.stp{border-radius:var(--m-r)}
.readout,.eq-block,.eqgrid .eqc,.eqgrid .eqn{border-radius:14px}
.intuit{background:color-mix(in srgb,var(--m-acc) 11%,var(--surface));border-left:4px solid var(--m-acc);border-radius:0 var(--m-r) var(--m-r) 0}
.intuit .k{color:var(--m-acc-d)}
.assume{background:color-mix(in srgb,var(--m-lav) 13%,var(--surface));border:1px solid color-mix(in srgb,var(--m-lav) 38%,var(--line));border-radius:var(--m-r)}
.assume h3,.assume .k{color:var(--m-acc-d)}
.coach{background:color-mix(in srgb,var(--m-acc) 9%,var(--surface));border:1px solid color-mix(in srgb,var(--m-acc) 32%,var(--line));border-radius:14px}
.coach b{color:var(--m-acc-d)}
.try{background:color-mix(in srgb,var(--m-acc) 8%,var(--surface));border:1px solid color-mix(in srgb,var(--m-acc) 28%,var(--line));border-radius:var(--m-r)}
.oops{border-radius:0 var(--m-r) var(--m-r) 0}
.ttip{border-radius:var(--m-r)}
.tag{background:color-mix(in srgb,var(--m-acc) 9%,var(--surface));border-color:color-mix(in srgb,var(--m-acc) 30%,var(--line));color:var(--m-acc-d)}
.mod:hover{border-color:var(--m-acc)}
details summary{color:var(--m-acc-d)}
.quiz .opts button{border-radius:12px}
.quiz .opts button:hover{background:color-mix(in srgb,var(--m-acc) 10%,var(--surface))}
.steps{background:transparent;-webkit-backdrop-filter:none;backdrop-filter:none}
.steps.stuck,.steps[data-stuck]{background:color-mix(in srgb,var(--bg) 82%,transparent);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
'''
PTR_CSS = r'''/* Pointer feel (shared with the Intulab landing page): module cards tilt toward the mouse and light up; main buttons get a quick light sweep. Mouse and trackpad only; off for reduced motion. */
@media (hover:hover) and (pointer:fine){
  a.mod:hover{transform:perspective(900px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) translateY(-3px);
    background-image:radial-gradient(220px circle at var(--mx,50%) var(--my,50%),color-mix(in srgb,var(--accent,#5CB8FF) 15%,transparent),transparent 70%)}
  .btn.primary{position:relative;overflow:hidden}
  .btn.primary::after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(100deg,transparent 30%,rgba(255,255,255,.28) 50%,transparent 70%);transform:translateX(-120%);transition:transform .7s}
  .btn.primary:hover::after{transform:translateX(120%)}
}
@media (prefers-reduced-motion:reduce){a.mod:hover{transform:translateY(-3px)}.btn.primary::after{display:none}}
'''
PTR_JS = r'''/* Pointer feel (same as the Intulab landing page): module cards tilt toward the mouse and light up. Mouse and trackpad only, never with reduced motion. */
(function pointerFeel(){var fine=matchMedia('(hover: hover) and (pointer: fine)'),rm=matchMedia('(prefers-reduced-motion: reduce)');if(!fine.matches||rm.matches)return;
  addEventListener('pointermove',function(e){if(e.pointerType!=='mouse')return;var c=e.target.closest&&e.target.closest('a.mod');if(c){var r=c.getBoundingClientRect(),px=(e.clientX-r.left)/r.width,py=(e.clientY-r.top)/r.height;
      c.style.setProperty('--mx',(px*100).toFixed(1)+'%');c.style.setProperty('--my',(py*100).toFixed(1)+'%');c.style.setProperty('--ry',((px-.5)*5).toFixed(2)+'deg');c.style.setProperty('--rx',((.5-py)*5).toFixed(2)+'deg');}},{passive:true});
  document.addEventListener('pointerout',function(e){var c=e.target.closest&&e.target.closest('a.mod');if(c&&!c.contains(e.relatedTarget)){c.style.removeProperty('--rx');c.style.removeProperty('--ry');}});})();
'''
APP_MORE_END = '<span class="tl">More labs</span></a>'

AP_GROUPS = """const GROUPS=[
  {w:'Optional',ch:'',name:'Math toolkit',ids:['deriv','integ','products','diffeq']},
  {w:'Unit 1',ch:'U1',name:'Kinematics',ids:['graphs','constant','variable','vectors','projectile','relative']},
  {w:'Unit 2',ch:'U2',name:'Force and translational dynamics',ids:['forces','friction','pulleys','circular','dynamics','com','gfield']},
  {w:'Unit 3',ch:'U3',name:'Work, energy and power',ids:['energy','loop']},
  {w:'Unit 4',ch:'U4',name:'Linear momentum',ids:['momentum','impulse']},
  {w:'Unit 5',ch:'U5',name:'Torque and rotational dynamics',ids:['torque','rotation']},
  {w:'Unit 6',ch:'U6',name:'Energy and momentum of rotating systems',ids:['angular','gravity']},
  {w:'Unit 7',ch:'U7',name:'Oscillations',ids:['shm']},
  {w:'Beyond AP C',ch:'',name:'Damping and waves',ids:['damped','waves','interf','sound','beats','fourier']}
];"""


def ap_version(text):
    p = Page(text, 'ap')
    shared_edits(p)
    # side rail
    p.rep('For Physics 1 and AP Physics C: Mechanics.', 'For AP Physics C: Mechanics.')
    p.rep('<span class="mapnote">Week numbers are mapped to the PHY 103 schedule at Princeton.</span>', '')
    p.rep('<span class="mapnote">Unofficial study aid. Not affiliated with Princeton University or the College Board.</span>',
          '<span class="mapnote">Unofficial study aid. Not affiliated with the College Board.</span>')
    # hero
    p.rep('<span class="tag pu">Physics 1</span><span class="tag ap">AP Physics C: Mechanics</span>',
          '<span class="tag ap">AP Physics C: Mechanics</span><span class="tag calc">Calculus-based</span>')
    p.rep("An interactive module for every topic in calculus-based Physics 1, from kinematics and Newton's laws through rotation, orbits, oscillations and waves, each mapped to AP Physics C: Mechanics.",
          "An interactive module for every topic in AP Physics C: Mechanics, from kinematics and Newton's laws through rotation, orbits and oscillations, plus waves as an extra.")
    p.rep('<p class="heronote">The weeks follow the order of PHY 103 at Princeton University, so Princeton students can study along with the course. This is an independent, unofficial study aid. It is not affiliated with, reviewed by, or endorsed by Princeton University, its Physics Department, or the College Board.',
          '<p class="heronote">The modules follow the AP Physics C: Mechanics units in order. This is an independent, unofficial study aid. It is not affiliated with, reviewed by, or endorsed by the College Board.')
    # overview
    p.rep('<p><b>Physics 1:</b> follow the weeks in order alongside your class.</p><p><b>AP Physics C:</b> do Weeks 1–9, skip damping and waves, then work through the <a href="#frq">FRQ practice</a> section.</p>',
          '<p><b>In order:</b> work through Units 1 to 7. Damping and waves at the end go beyond AP C, so they are optional.</p><p><b>Free response:</b> when you finish the units, work through the <a href="#frq">FRQ practice</a> section.</p>')
    p.rep('Modules by week</h2>', 'Modules by unit</h2>')
    p.rep('AP Physics C: Mechanics covers everything through simple harmonic motion. Damping, resonance and waves are Physics 1 only. <span class="mapnote">Week numbers are mapped to the PHY 103 schedule at Princeton. Unofficial study aid, not affiliated with Princeton University or the College Board.</span>',
          'Each row is one unit of AP Physics C: Mechanics. The last group, damping and waves, goes beyond AP C: good extras, not on the exam.')
    p.rep('<th id="map-col">Week</th>', '<th id="map-col">Unit</th>')
    # groups: AP units instead of PHY 103 weeks
    p.cut('const GROUPS=[', '];', new=AP_GROUPS)
    # cross-references inside lessons
    for old, new in [('simple harmonic motion in Week 9.', 'simple harmonic motion in Unit 7.'),
                     ('flew through the air (Week 1)', 'flew through the air (Unit 1)'),
                     ('<dd>Week 6, <a href="#rotation">Rolling</a> (Pulleys revisited)', '<dd>Unit 5, <a href="#rotation">Rolling</a> (Pulleys revisited)'),
                     ('<dd>Week 6, <a href="#rotation">Rolling</a>: a rolling', '<dd>Unit 5, <a href="#rotation">Rolling</a>: a rolling'),
                     ('pulleys were massless (Week 2)', 'pulleys were massless (Unit 2)'),
                     ('loop-the-loop cart slid (Week 4)', 'loop-the-loop cart slid (Unit 3)'),
                     ('no torque about the Sun (Week 8)', 'no torque about the Sun (Unit 6)'),
                     ('<dd>Week 10, <a href="#damped">', '<dd>Beyond AP C, <a href="#damped">'),
                     ('no friction or air resistance (Week 9)', 'no friction or air resistance (Unit 7)')]:
        p.rep(old, new)
    p.rep('Week 2 model', 'Unit 2 model', count=4)
    # review views
    p.rep('<span class="tag ap">Physics 1 + AP C</span>', '<span class="tag ap">AP Physics C</span>', count=2)
    p.rep('All weeks<span class="tag ap">AP C style</span><span class="tag pu">Physics 1 style</span>',
          'All units<span class="tag ap">AP C style</span><span class="tag na">Beyond AP C</span>')
    p.rep("'AP C':'Physics 1'", "'AP C':'Beyond AP C'")
    p.rep('covering every week of the course', 'covering every unit of the course')
    p.rep('Build a mixed problem set from the weeks your exam covers.', 'Build a mixed problem set from the units your exam covers.')
    p.rep('Which weeks does your exam cover?', 'Which units does your exam cover?')
    p.rep('id="ex-weeks" role="group" aria-label="Weeks"', 'id="ex-weeks" role="group" aria-label="Units"')
    # formula sheet
    p.rep('plus waves for Physics 1.', 'plus waves (beyond AP C).')
    p.rep('Your Physics 1 class may give you a different sheet on exams.', 'Your class may give you a different sheet on tests.')
    p.rep('<span class="tag na">Physics 1 only</span>', '<span class="tag na">Beyond AP C</span>', count='all')
    # one label for the extras, matching the menu group
    p.rep("ap:'Not on AP C'", "ap:'Beyond AP C'", count='all')
    p.rep('<span class="tag na">Not on AP C Mech</span>', '<span class="tag na">Beyond AP C</span>', count='all')
    # reports
    p.rep('(Physics 1 + AP Physics C: Mechanics)', '(AP Physics C: Mechanics)')
    # Intulab app: install tags and offline support (sw.js lives in this repo)
    p.rep('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n',
          '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + APP_HEAD)
    p.rep(APP_MORE_END, APP_MORE_END + APP_BTN)
    p.rep('<a class="btn" href="#practice" style="text-decoration:none">Go to the practice set</a>', '<a class="btn" href="#practice" style="text-decoration:none">Go to the practice set</a><button type="button" class="btn appbtn2" hidden aria-haspopup="dialog">Get the app</button>')
    p.rep('\n    <nav class="nav" id="nav"', '\n    ' + APP_DLG.rstrip('\n') + '\n    <nav class="nav" id="nav"')
    p.rep('/* link back to the Intulab landing page */', APP_CSS.lstrip('\n') + PTR_CSS + '/* link back to the Intulab landing page */')
    i = p.s.rindex('</script>')
    p.s = p.s[:i] + APP_REG + APP_JS + PTR_JS + p.s[i:]
    j = p.s.rindex('</style>')
    p.s = p.s[:j] + APPEAL_CSS + p.s[j:]
    return p.s


PHY_FORMULAS_CSS = """
/* Key formulas page (PHY 103 version) */
.fsp{max-width:820px}
.fsp h3{font:500 12px var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:22px 0 6px}
.fsp dl{margin:0;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 16px;align-items:baseline;border-top:1px solid var(--line);padding-top:8px}
.fsp dt{font-family:var(--f-math);font-size:17px;overflow-x:auto}
.fsp dt i{font-style:italic}
.fsp dd{margin:0;font-size:13px;color:var(--muted);text-align:right}
/* no AP unit tags on PHY 103 module headers and cards */
.view .head .eyebrow .tag.ap,.view .head .eyebrow .tag.na{display:none}
"""


PHY_STUDY_CSS = """
/* ---------------- PHY 103: the Multivariable Calculus Lab look ----------------
   Same tokens as MAT 201: light only, IBM Plex Sans / STIX Two Text / IBM Plex Mono, one blue accent,
   white cards on a plain gray page. Plot colors (x blue, v green, a red) keep their meaning; nothing decorative
   moves. The simulations still run. */
:root{
  color-scheme:light;
  --bg:#F4F6F8; --surface:#FFFFFF; --sunk:#F6F8FA; --ink:#18202B; --muted:#5A6676; --line:#DEE3EA; --grid:transparent; --accent:#2457A6;
  --cx:#2457A6; --cv:#2E8B57; --ca:#C2453A; --hot:#D9822B; --good:#2E8B57; --bad:#C2453A;
  --f-display:"IBM Plex Sans","Segoe UI",system-ui,sans-serif; --f-body:"IBM Plex Sans","Segoe UI",system-ui,sans-serif;
  --f-math:"STIX Two Text","Cambria Math","Times New Roman",serif; --f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  --shadow-1:none; --shadow-2:none;
  --h-font:var(--f-body); --h-w:600; --h-track:-.01em; --brand-w:700;
  --radius:10px; --btn-bg:var(--accent); --btn-fg:#FFFFFF; --btn-font:var(--f-body); --btn-case:none; --btn-track:0; --btn-size:14px;
  --nav-bg:#E6EEFA; --nav-fg:var(--accent); --lab-c:var(--muted); --ro-c:var(--ink);
  --cap-font:var(--f-body); --cap-style:normal; --cap-size:13px; --page-grid:none;
  --fig-tag:none; --fig-tag-c:var(--muted); --hl-style:normal; --h2-rule:1px solid var(--line); --h2-bar:none; --lift:0px;
}
html{background:var(--bg)}
body{font-size:15.5px;line-height:1.55}
*,::before,::after{animation:none!important}
.nav .ind,.steps .ind,.nav a,.rmeter i,.mod,.modnav a,.btn,.searchbtn,.morelabs,details summary::before{transition:none!important}
.mod:hover,.modnav a:hover,.btn:active,.searchbtn:active{transform:none!important}
h1{font-size:clamp(28px,3.6vw,38px);line-height:1.15;font-weight:600}
.view:not(#v-overview) .head h1{font-size:clamp(26px,3.2vw,34px)}
h2{font-size:clamp(20px,2.4vw,24px);font-weight:600}
.mod h3,.modgroup .gtitle,.start h3,.modnav a strong{font-weight:600}
.modgroup .gtitle{font-size:19px}.mod h3{font-size:16px}
.hero h1 .hl{color:var(--ink);font-style:normal}
.brand{font-size:18px}
/* labels: small caps in the body font, like the MAT 201 boxes */
.eyebrow,.tag,.nav .grp,.labbar .title,.intuit .k,.note b,.try h3,.oops h3,.example h3,.sorter h3,.assume h3,.assume dt,.coach b,.ttip h3,
.fs h3,.fsp h3,.modnav a span,.mod .n,.mod .prog,.railprog,.steps a .sn,th,.readout span,.eqgrid .eqn small,.mapnote,.rp .ri .meta{
  font-family:var(--f-body)!important;font-weight:600;letter-spacing:.08em}
.mapnote,.railprog,.mod .prog,.mod .n{font-weight:400;letter-spacing:0;font-size:12px}
.eqgrid .eqn small,.readout span,.assume dt{letter-spacing:.04em}
select,input[type=text]{font-family:var(--f-body)}
.credit-row{font-size:13.5px}
/* one neutral card style; color only where it carries meaning */
.lab,.example,.sorter,.frq,.strobe,.quiz,.prob,.start>div,.modnav a,.tablewrap,.try,.assume,.ttip,.v3{background:var(--surface);border:1px solid var(--line);box-shadow:none}
.lab::before,.strobe::before,.mod::before,.modgroup .gtitle::before{display:none}
.start>div:nth-child(n){border-top:1px solid var(--line)}
.modgroup{--c:var(--line)}
.mod{border-top:0}
.mod:hover{border-color:var(--accent)}
.intuit{background:#E6EEFA;border-left:3px solid var(--accent)}
.intuit .k{color:var(--accent)}
.oops{background:#FCEFE0;border-left-color:var(--hot)}
.oops h3{color:#9A5512}
.assume.upgrade,.assume.fornow{background:var(--sunk);border:1px solid var(--line)}
.assume.upgrade h3,.assume.fornow h3,.example h3,.sorter h3,.try h3{color:var(--muted)}
.coach{background:var(--sunk);border-color:var(--line)}
.coach b{color:var(--accent)}
.eqn{background:var(--sunk);border:1px solid var(--line)}
.tag,.tag.pu,.tag.calc,.tag.ap{color:var(--muted);border-color:var(--line);background:var(--surface)}
.rmeter i{background:var(--accent)}
.mp-hero{background:var(--sunk)}
.wrap>.head h2{border-top:0;padding-top:0}
.btn.primary:hover{box-shadow:none;filter:brightness(1.08)}
.fx,.bubble,.cele{display:none!important}
"""


def phy_version(text):
    p = Page(text, 'phy')
    shared_edits(p)
    # name
    p.rep('<title>Mechanics Lab</title>', '<title>PHY 103 Lab</title>')
    p.rep('aria-label="Mechanics Lab home"', 'aria-label="PHY 103 Lab home"')
    p.rep('<span>Mechanics Lab</span>', '<span>PHY 103 Lab</span>')
    # side rail
    p.rep('For Physics 1 and AP Physics C: Mechanics.', 'For PHY 103: calculus-based mechanics and waves.')
    p.rep('Week numbers are mapped to the PHY 103 schedule at Princeton.</span>', 'Weeks follow the PHY 103 schedule.</span>')
    p.rep('<span class="mapnote">Unofficial study aid. Not affiliated with Princeton University or the College Board.</span>',
          '<span class="mapnote">Unofficial study aid. Not affiliated with Princeton University.</span>')
    p.rep('Visit counts are anonymous (GoatCounter, no cookies).', 'Nothing is counted or tracked.')
    p.rep('<span class="mapnote">AP® and Advanced Placement® are trademarks registered by the College Board, which is not affiliated with, and does not endorse, this site.</span>', '')
    p.rep('/intulab/privacy.html', '/princeton-labs/privacy.html', count=2)
    p.rep('/intulab/terms.html', '/princeton-labs/terms.html', count=2)
    p.rep('<a class="morelabs" href="/intulab/" aria-label="More labs from Intulab">', '<a class="morelabs" href="/princeton-labs/" aria-label="More Princeton labs">')
    # credit as plain text: "Built by Jiarui Li · Princeton Class of 2030 · a student project", no LinkedIn
    p.cut('<span class="mapnote"><a class="li-link"', 'LinkedIn</a></span>')
    p.cut('<span class="credit-row">', 'LinkedIn</a></span>', new='<span class="credit-row">Built by Jiarui Li · Princeton Class of 2030 · a student project</span>')
    p.s, n = re.subn(r'(?:(?:\.rail )?\.li-link[^{]*\{[^}]*\}\n)+', '', p.s)
    if n != 1: sys.exit(f'[phy] expected the LinkedIn styles, found {n}')
    # look: match Multivariable Calculus Lab (fonts, light only, calm motion)
    i = p.s.find('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'); j = p.s.find('>', i) + 1
    p.rep(p.s[i:j], '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=STIX+Two+Text:ital,wght@0,500;0,600;1,500&family=IBM+Plex+Mono:wght@400;500&display=swap">')
    p.rep('.rv{opacity:1;transform:none}}\n</style>', '.rv{opacity:1;transform:none}}\n' + PHY_STUDY_CSS + '</style>')
    p.cut('<button type="button" class="themebtn" id="theme-btn"', '</button>')
    p.cut('/* ---------------- Theme switch: auto (follows the device), light, dark ---------------- */', '/* ---------------- Feedback motion', include_end=False,
          new="/* light theme only, like Multivariable Calculus Lab */\ndocument.documentElement.setAttribute('data-theme','light');\n")
    # decorative motion off (sparks, bubbles, count-ups, card flips, scroll reveals); the simulations keep running
    p.rep("const REDUCE=matchMedia('(prefers-reduced-motion: reduce)').matches;", "const REDUCE=matchMedia('(prefers-reduced-motion: reduce)').matches,CALM=true;")
    for old, new in [('spray(x,y,n,o={}){if(REDUCE)', 'spray(x,y,n,o={}){if(CALM)'), ('function burst(el,n=14){if(REDUCE', 'function burst(el,n=14){if(CALM'),
                     ('function bubble(el,text,bad){if(REDUCE)', 'function bubble(el,text,bad){if(CALM)'), ('function flipFrom(el,from,ms=480){if(REDUCE', 'function flipFrom(el,from,ms=480){if(CALM'),
                     ('function countUp(el,to){if(REDUCE)', 'function countUp(el,to){if(CALM)'), ("closest('summary');if(!s||REDUCE)", "closest('summary');if(!s||CALM)"),
                     ('(function reveal(){if(REDUCE', '(function reveal(){if(CALM')]:
        p.rep(old, new)
    # hero
    p.rep('<span class="tag pu">Physics 1</span><span class="tag ap">AP Physics C: Mechanics</span>',
          '<span class="tag pu">PHY 103</span><span class="tag calc">Calculus-based</span>')
    p.rep("An interactive module for every topic in calculus-based Physics 1, from kinematics and Newton's laws through rotation, orbits, oscillations and waves, each mapped to AP Physics C: Mechanics.",
          "An interactive module for every topic in PHY 103, in the order of the course: kinematics and Newton's laws through rotation, orbits, oscillations and waves.")
    p.rep('<div class="countdown" id="ap-count" aria-live="polite"></div>', '')
    p.rep('<p class="heronote">The weeks follow the order of PHY 103 at Princeton University, so Princeton students can study along with the course. This is an independent, unofficial study aid. It is not affiliated with, reviewed by, or endorsed by Princeton University, its Physics Department, or the College Board. Use it to study, not on graded work. AP® and Advanced Placement® are trademarks registered by the College Board, which is not affiliated with, and does not endorse, this site.</p>',
          '<p class="heronote">The modules follow the week-by-week order of PHY 103 at Princeton University, so you can study along with the course. This is an independent, unofficial study aid. It is not affiliated with, reviewed by, or endorsed by Princeton University or its Physics Department. Use it to study, not on graded work, and follow the course\'s collaboration rules.</p>')
    p.rep(' · matches the May 2027 AP exam format', '')
    # overview
    p.rep('<p><b>Physics 1:</b> follow the weeks in order alongside your class.</p><p><b>AP Physics C:</b> do Weeks 1–9, skip damping and waves, then work through the <a href="#frq">FRQ practice</a> section.</p>',
          '<p><b>Each week:</b> do that week\'s modules alongside the lectures and problem sets.</p>')
    p.rep('<p><b>Before an exam:</b>', '<p><b>Before a midterm or final:</b>')
    p.rep('<p>Stuck on notation? Open the <b>Formula sheet</b> button at the bottom right.</p>',
          '<p>Stuck on notation? The <a href="#formulas">Key formulas</a> page in the menu lists the main equations.</p>')
    p.rep('AP Physics C: Mechanics covers everything through simple harmonic motion. Damping, resonance and waves are Physics 1 only. <span class="mapnote">Week numbers are mapped to the PHY 103 schedule at Princeton. Unofficial study aid, not affiliated with Princeton University or the College Board.</span>',
          'Each row is one week of PHY 103. <span class="mapnote">Unofficial study aid, not affiliated with Princeton University.</span>')
    # formula drawer -> Key formulas page
    p.cut('<div class="fs-scrim" id="fs-scrim" aria-hidden="true"></div>', '</button>')
    aside = p.cut('<aside class="fs" id="fs" aria-label="Formula sheet" aria-hidden="true">', '</aside>')
    body = aside[aside.find('<div class="body">') + len('<div class="body">'):aside.rfind('</div>')]
    body = re.sub(r'\s*<p class="fine"[^>]*>.*?</p>', '', body, count=1, flags=re.S)
    body = body.replace('<span class="tag na">Physics 1 only</span>', '')
    page = ('  <!-- ============ KEY FORMULAS ============ -->\n  <section class="view" id="v-formulas" hidden>\n    <div class="wrap">\n'
            '      <div class="head"><div class="eyebrow">Review<span class="tag pu">PHY 103</span></div><h1>Key formulas</h1>'
            '<p class="lede">The main equations of the course in one place, written for this site. It is a study page, not an official exam sheet, so check what your exams allow.</p></div>\n'
            '      <div class="fsp">' + body + '</div>\n    </div>\n  </section>\n\n')
    # FRQ view -> gone; Key formulas page takes its place
    p.cut('<!-- ============ FRQ ============ -->', '</section>', new=page.lstrip())
    # exam format box
    p.cut('      <div class="exfmt" aria-labelledby="exfmt-h">', '</p>\n      </div>\n')
    # review views
    p.rep('<span class="tag ap">Physics 1 + AP C</span>', '<span class="tag pu">PHY 103</span>', count=2)
    p.rep('All weeks<span class="tag ap">AP C style</span><span class="tag pu">Physics 1 style</span>', 'All weeks')
    p.rep('Build a mixed problem set from the weeks your exam covers.', 'Build a mixed problem set from the weeks your midterm or final covers.')
    p.rep('Which weeks does your exam cover?', 'Which weeks does your midterm or final cover?')
    p.rep("<span class=\"tag ${apTag(p.topic)}\">${apTag(p.topic)==='ap'?'AP C':'Physics 1'}</span>", '')
    p.rep('<span class="tag ${apTag(id)}">${m.ap}</span>', '<span></span>', count=2)
    # AP unit tags on module headers, and the AP labels in the module list
    p.s, n = re.subn(r'<span class="tag (?:ap|na)">(?:AP C[^<]*|Not on AP C[^<]*|Beyond AP C)</span>', '', p.s)
    if n < 20: sys.exit(f'[phy] expected the module AP tags, found {n}')
    i = p.s.find('const MODS={'); j = p.s.find('};', i) + 2
    p.s = p.s[:i] + re.sub(r",ap:(['\"])[^'\"]*\1", ",ap:''", p.s[i:j]) + p.s[j:]
    p.rep('covers that case, and AP C free-response questions use it often.', 'covers that case, and exam problems use it often.')
    # navigation: Key formulas instead of FRQ practice
    p.rep('<a href="#frq" data-view="frq">AP C FRQ practice</a>', '<a href="#formulas" data-view="formulas">Key formulas</a>')
    p.rep('<option value="frq">AP C FRQ practice</option>', '<option value="formulas">Key formulas</option>')
    p.rep("const VIEWS=['overview',...Object.keys(MODS),'practice','frq','methods','exam','review'];",
          "const VIEWS=['overview',...Object.keys(MODS),'practice','methods','exam','review','formulas'];")
    # scripts that only exist for AP content
    p.cut('/* ---------------- FRQ section ---------------- */', '/* ---------------- Formula sheet drawer ---------------- */', include_end=False)
    p.cut('/* ---------------- Formula sheet drawer ---------------- */', '/* ---------------- Free-body diagrams', include_end=False)
    p.cut('/* ---------------- AP exam countdown ----------------', '/* light theme only, like Multivariable Calculus Lab */', include_end=False)
    i = p.s.find('(function analytics(){'); c = p.s.rfind('/*', 0, i)
    p.cut(p.s[c:i + len('(function analytics(){')], '})();\n')
    # reports go to this site's own repo
    p.rep("const REPO='https://github.com/jiacode2030/intulab-feedback';", "const REPO='https://github.com/jiacode2030/phy103-lab';")
    p.rep("const COURSE='Mechanics Lab',COURSE_LABEL='course:mechanics'", "const COURSE='PHY 103 Lab',COURSE_LABEL=''")
    p.rep("REPO+'/issues/new?labels='+encodeURIComponent(COURSE_LABEL)+'&title='", "REPO+'/issues/new?title='")
    p.rep('(Physics 1 + AP Physics C: Mechanics)', '(PHY 103)')
    # styles, and separate saved progress from the AP site (same origin)
    p.rep('/* link back to the Intulab landing page */', PHY_FORMULAS_CSS.lstrip('\n') + '/* link back to the Intulab landing page */')
    p.rep("'kin-", "'phy-", count='all')
    return p.s


def check_js(html, name):
    """node --check every inline script."""
    for k, js in enumerate(re.findall(r'<script>(.*?)</script>', html, re.S)):
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
            f.write(js)
        r = subprocess.run(['node', '--check', f.name], capture_output=True, text=True)
        if r.returncode:
            print(r.stderr); sys.exit(f'[{name}] JS syntax error in script {k}')


def scan(html, name, banned, allowed=()):
    text = html
    for a in allowed:
        text = text.replace(a, '')
    hits = [(w, text.count(w)) for w in banned if w in text]
    if hits:
        sys.exit(f'[{name}] leftover words from the other site: {hits}')


def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'{path}: {len(html)//1024} KB')


def main():
    src = open(SRC, encoding='utf-8').read()
    args = sys.argv[1:]
    want_ap = not args or args[0] == '--all'
    phy_dir = args[1] if len(args) > 1 and args[0] in ('--phy', '--all') else None
    if want_ap:
        ap = ap_version(src)
        check_js(ap, 'ap')
        scan(ap, 'ap', ['PHY 103', 'Physics 1', 'Princeton University', 'Week ', 'week-by-week'],
             allowed=['Princeton Class of 2030'])
        write(os.path.join(ROOT, 'index.html'), ap)
    if phy_dir:
        phy = phy_version(src)
        check_js(phy, 'phy')
        scan(phy, 'phy', ['AP C', 'AP Physics', 'AP®', 'Advanced Placement', 'College Board', 'goatcounter', 'intulab', "'kin-", 'ap-count', 'LinkedIn', 'li-link', 'Created by', 'theme-btn', 'manifest', 'serviceWorker', 'app-btn', 'Get the app'])
        write(os.path.join(os.path.abspath(phy_dir), 'index.html'), phy)


if __name__ == '__main__':
    main()
