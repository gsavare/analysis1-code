# Mathematical Analysis 1 — the code

The computations that go with the course. Two ways in, depending on what you
want.

## Just look at it — nothing to install

**https://giuseppesavare.com/analysis1-code/**

Each notebook runs Python inside your browser: no installation, no account, no
sign-up. The first load takes a few seconds while the interpreter arrives, then
everything happens on your own machine. It works on a phone or a tablet too.

Change the numbers. That is the point of them being there.

## Run it yourself

`analysis.py` is the toolbox and the `lecNN_experiments.py` scripts reproduce
every number quoted in the corresponding lecture. They use the **standard
library only** — no installation, any `python3`:

```
python3 lec01_experiments.py
```

The rule of the course is that numbers on the slides are computed here, not
typed. If a slide and this code ever disagree, the code is right and the slide
is a bug.

## What is in each lecture

| | |
|---|---|
| `lec01_experiments.py` | what a `float64` really holds; why `0.1 + 0.2 != 0.3`; the spacing between machine numbers; the Babylonian iteration in exact fractions beside the same iteration in floating point |
| `lec02_experiments.py` | trapping a number between shrinking rational intervals: digit by digit, by bisection, and by Newton — three algorithms, one real number |
| `lec03_experiments.py` | the separation theorem by bisection, checked rather than asserted: the bisection that *defines* √2 and the one that *proves* completeness produce identical intervals at every step |

## Editing the notebooks

The notebooks are plain `.py` files — no embedded JSON, no stored output — so
they read and diff like any other source file.

```
make venv              once
make run NB=lec01      run it as an app, at native speed
make edit NB=lec01     open it for editing
make notebooks         export the browser version into build/
```
