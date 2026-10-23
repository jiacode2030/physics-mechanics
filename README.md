# Mechanics Lab: AP Physics C: Mechanics

An interactive, intuition-first study site for AP Physics C: Mechanics, part of [AP Labs](https://jiacode2030.github.io/ap-labs/).

Each topic gets its own module with:

- a live simulation, showing the actual motion before any graphs
- a "Try this" section: guess first, then check
- a step-by-step worked example with a free-body diagram
- common mistakes
- a "Check yourself" quiz
- practice problems with randomized numbers

Modules are grouped by the seven AP Physics C: Mechanics units. Damping and waves come last, under "Beyond AP C". The review sections are "Which principle?", exam review (with the exam format), a mistakes queue and FRQ practice. A formula sheet opens from the bottom-right corner.

The site is one HTML file (`index.html`). Open it in a browser, or visit the GitHub Pages site.

> **Unofficial study aid.** Not affiliated with, reviewed by, or endorsed by the College Board.
>
> **Use it to study, not on graded work.**
>
> AP® and Advanced Placement® are trademarks registered by the College Board, which is not affiliated with, and does not endorse, this site.

## Two sites from one source

`src/site.html` is the shared page: every module, simulation, worked example, quiz and problem. `build.py` turns it into two sites:

| | This repo (`index.html`) | [`phy103-lab`](https://github.com/jiacode2030/phy103-lab) |
|---|---|---|
| Part of | AP Labs | Princeton Labs |
| Menu | AP Physics C units | PHY 103 weeks |
| AP countdown, formula sheet, FRQ practice, exam format | yes | no (a Key formulas page instead) |
| Visit counts | GoatCounter (`aplabs`) | none |
| Saved progress keys | `kin-` | `phy-` |
| Reports | `ap-labs-feedback` | the `phy103-lab` repo's issues |

Edit `src/site.html`, never `index.html`, then rebuild:

```
python3 build.py --all ../phy103-lab   # writes index.html here and ../phy103-lab/index.html
```

`build.py` makes each site's changes as exact text edits. If an edit no longer matches the source, it stops with an error. It then checks the JavaScript and scans each output for words that belong to the other site, such as "PHY 103" on the AP site or "AP C" on the PHY 103 site. Commit and push both repos.

## Reporting a problem

Every module and practice problem has a **Report an issue** link. On this site it opens a pre-filled GitHub issue. Issues go to the shared [AP Labs feedback](https://github.com/jiacode2030/ap-labs-feedback/issues) tracker, labelled `course:mechanics`. You can also [open one directly](https://github.com/jiacode2030/ap-labs-feedback/issues/new/choose).

The **More AP labs** link in the side rail goes to the [AP Labs](https://jiacode2030.github.io/ap-labs/) landing page.

## Privacy

- Progress (modules done, solved problems, review queue, theme) is saved only in your browser's local storage.
- The public site counts visits per page with [GoatCounter](https://www.goatcounter.com): anonymous, no cookies.
- The Report button opens a pre-filled GitHub issue, which is public. Don't include personal information.
- Full details: [Privacy policy](https://jiacode2030.github.io/ap-labs/privacy.html) and [Terms of use](https://jiacode2030.github.io/ap-labs/terms.html).

## Checks

These need Node.js and Playwright:

- `node tests/check6.js [file]` visits every page (of `index.html`, or the file you name, e.g. `../phy103-lab/index.html`) at desktop and phone width. It looks for overflow, blank canvases, NaN values and broken "Set it up for me" buttons.
- `node tests/probdump.js` prints one generated sample of every practice problem, so you can check the answers.
