# Physics 1 + AP Physics C: Mechanics

An interactive, intuition-first study site for calculus-based Physics 1 and AP Physics C: Mechanics.

Each topic gets its own module with:

- a live simulation, showing the actual motion before any graphs
- a "Try this" section: guess first, then check
- a step-by-step worked example with a free-body diagram
- common mistakes
- a "Check yourself" quiz
- practice problems with randomized numbers

The review sections are "Which principle?", exam review, a mistakes queue and FRQ practice. A formula sheet opens from the bottom-right corner.

The whole site is one HTML file (`index.html`) with no build step. Open it in a browser, or visit the GitHub Pages site.

> **Unofficial study aid.** The week numbers are mapped to the PHY 103 schedule at Princeton, but this site is not affiliated with, reviewed by, or endorsed by Princeton University, its Physics Department, or the College Board.
>
> **Use it to study, not on graded work.**
>
> AP® and Advanced Placement® are trademarks registered by the College Board, which is not affiliated with, and does not endorse, this site.

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

- `node tests/check6.js` visits every page at desktop and phone width. It looks for overflow, blank canvases, NaN values and broken "Set it up for me" buttons.
- `node tests/probdump.js` prints one generated sample of every practice problem, so you can check the answers.
