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

## Reporting a problem

Every module and practice problem has a **Report an issue** link. On this site it opens a pre-filled GitHub issue. You can also [open an issue](https://github.com/jiacode2030/physics-mechanics/issues/new) directly.

## Checks

These need Node.js and Playwright:

- `node tests/check6.js` visits every page at desktop and phone width. It looks for overflow, blank canvases, NaN values and broken "Set it up for me" buttons.
- `node tests/probdump.js` prints one generated sample of every practice problem, so you can check the answers.
