"""Lecture 2, as a notebook the students can run in a browser.

    make numerics-edit NB=lec02     to write it
    make numerics                   to export it for the web

The arithmetic is not repeated here: every number still comes from
`numerics/analysis.py`, exactly as in `numerics/lec02_experiments.py`.  What
this file adds is the knob -- the reader chooses the algorithm, the step, the
number of digits, and watches the intervals close in.

Three knobs, one per claim the slides can only assert:
  1. a nesting algorithm, step by step -- the lengths are infinitesimal;
  2. three algorithms, one number -- the intervals always meet;
  3. the greedy digits -- an expansion is READ OFF an algorithm, not chosen.
The carry experiment (why digit strings cannot be added) stays in
lec02_experiments.py, section 7.
"""

# /// script
# requires-python = ">=3.9"
# dependencies = ["marimo", "matplotlib"]
# ///
#
# The block above records the dependencies for a local `uv`/`--sandbox` run.
# It does NOT reach the browser: the WASM export keeps only the code from
# `import marimo` down, and works out what to install by reading the import
# statements.  Hence the importlib calls in the setup cell -- see there.

import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
async def _(mo):
    # The toolbox lives in numerics/, one level up.  Running from the repo we
    # just add that directory to the path; running in the browser there is no
    # repo, so we fetch the copy that `make numerics` publishes beside this
    # page.  Either way the functions below are the same ones the slides use.
    import sys
    import os
    import importlib

    # Three modules below are fetched through importlib rather than with a
    # plain `import`.  In the browser marimo decides what to install by
    # reading the notebook's import statements and handing the names to
    # micropip; `js` and `pyodide.http` are built into Pyodide and `analysis`
    # is this course's own file, so all three would be looked up on PyPI, not
    # found, and the failure would take the real dependencies down with it.
    # Kept dynamic, they are invisible to that scan and simply work.
    if sys.platform == "emscripten":
        js = importlib.import_module("js")
        pyodide_http = importlib.import_module("pyodide.http")

        # The cells run inside a web worker whose own URL is <site>/assets/
        # worker-*.js, so a relative fetch would look in assets/.  Cut the
        # path back to the directory holding index.html, wherever the site is
        # mounted, and take analysis.py from there.
        _base = str(js.location.href).split("/assets/")[0].rstrip("/")
        _resp = await pyodide_http.pyfetch(f"{_base}/analysis.py")
        with open("analysis.py", "w") as _fh:
            _fh.write(await _resp.string())
        sys.path.insert(0, os.getcwd())
    else:
        sys.path.insert(0, str(mo.notebook_dir().parent))

    from fractions import Fraction

    # `from matplotlib import pyplot`, not `import matplotlib.pyplot`: the
    # package scanner turns a dotted import into a dotted package name and
    # then asks PyPI for "matplotlib-pyplot", which does not exist.
    from matplotlib import pyplot as plt

    def sci(v, d=4):
        """A number in scientific notation, as LaTeX rather than as `1e-16`."""
        if float(v) == 0.0:
            return "0"
        _mant, _exp = f"{float(v):.{d}e}".split("e")
        return rf"{_mant} \times 10^{{{int(_exp)}}}"

    _analysis = importlib.import_module("analysis")
    babylonian = _analysis.babylonian
    return Fraction, babylonian, plt, sci, sys


@app.cell
def _(mo):
    mo.md(r"""
    # What a real number is

    A **nesting algorithm** is a sequence of intervals with rational
    endpoints,

    $$I_n=[a_n,b_n],\qquad I_{n+1}\subseteq I_n,$$

    whose lengths $b_n-a_n$ are *infinitesimal*: eventually below every
    positive rational.  A real number is a class of such algorithms, two of
    them being equivalent when their intervals always meet.

    Nothing below is a proof.  The point is to watch the definition work:
    the intervals close in, different algorithms agree, and the digits of an
    expansion turn out to be forced rather than chosen.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. One algorithm, step by step

    Three algorithms for $\sqrt2$ were built in the lecture.  Pick one and
    push the step up.  The endpoints stay **exact rationals** -- no floating
    point is involved -- and the length is what has to become infinitesimal.
    """)
    return


@app.cell
def _(mo):
    which = mo.ui.dropdown(
        options=["bisection (base 2)", "digits (base 10)", "Newton"],
        value="bisection (base 2)",
        label="algorithm",
    )
    step = mo.ui.slider(1, 12, value=6, label="step $n$")
    mo.hstack([which, step], justify="start", gap=2)
    return step, which


@app.cell
def _(Fraction, babylonian, mo, sci, step, which):
    def _bisection(n):
        _a, _b = Fraction(1), Fraction(2)
        _digits = ""
        for _ in range(n):
            _m = (_a + _b) / 2
            if _m * _m > 2:
                _b, _d = _m, "0"
            else:
                _a, _d = _m, "1"
            _digits += _d
        return _a, _b, rf"(1.{_digits})_2"

    def _decimal(n):
        # the largest truncation with t^2 < 2, one decimal place at a time
        _t = Fraction(1)
        for _k in range(1, n + 1):
            _unit = Fraction(1, 10 ** _k)
            while (_t + _unit) ** 2 < 2:
                _t += _unit
        return _t, _t + Fraction(1, 10 ** n), rf"({_t})_{{10}}"

    def _newton(n):
        _q = Fraction(2)
        for _q in babylonian(Fraction(2), Fraction(2), n):
            pass
        return 2 / _q, _q, r"\text{no digits: an interval, not an expansion}"

    _f = {"bisection (base 2)": _bisection,
          "digits (base 10)": _decimal,
          "Newton": _newton}[which.value]
    _a, _b, _label = _f(step.value)

    mo.md(rf"""
    $$I_{{{step.value}}}=\left[\,{_a},\ {_b}\,\right]$$

    | | |
    |---|---|
    | as decimals | $[{float(_a):.12f},\ {float(_b):.12f}]$ |
    | length | ${sci(_b - _a)}$ |
    | digits so far | ${_label}$ |

    Both endpoints are rationals, and $\sqrt2$ is trapped between them at
    every step -- yet no single interval ever contains it *alone*.  That is
    the whole difficulty the definition answers.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Bisection buys one binary place per step; Newton **doubles** the number
    of correct places each time.  Push the step up with Newton selected and
    the length falls off a cliff -- but both are nesting algorithms, and
    both name the same number.  Speed is not part of the definition.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. Three algorithms, one number

    Two algorithms represent the same real number when their intervals meet
    at **every** step.  Here are the three, at a step you choose.  Look for
    a step where the common part is empty.
    """)
    return


@app.cell
def _(mo):
    meet_step = mo.ui.slider(1, 10, value=4, label="compare at step $n$")
    meet_step
    return (meet_step,)


@app.cell
def _(Fraction, babylonian, meet_step, mo):
    _n = meet_step.value

    _a, _b = Fraction(1), Fraction(2)
    for _ in range(_n):
        _m = (_a + _b) / 2
        if _m * _m > 2:
            _b = _m
        else:
            _a = _m

    _t = Fraction(1)
    for _k in range(1, _n + 1):
        _u = Fraction(1, 10 ** _k)
        while (_t + _u) ** 2 < 2:
            _t += _u

    _q = Fraction(2)
    for _q in babylonian(Fraction(2), Fraction(2), _n):
        pass

    _fams = {
        "bisection": (_a, _b),
        "decimal": (_t, _t + Fraction(1, 10 ** _n)),
        "Newton": (2 / _q, _q),
    }
    _rows = "\n".join(
        rf"| {_k} | $[{float(_lo):.10f},\ {float(_hi):.10f}]$ |"
        for _k, (_lo, _hi) in _fams.items()
    )
    _lo = max(_x for _x, _ in _fams.values())
    _hi = min(_y for _, _y in _fams.values())
    _verdict = ("**they meet**" if _lo <= _hi
                else "**disjoint** -- which the lecture proves cannot happen")

    mo.md(rf"""
    | family | $I_{{{_n}}}$ |
    |---|---|
    {_rows}
    | **common part** | $[{float(_lo):.10f},\ {float(_hi):.10f}]$ |

    The three intervals overlap: {_verdict}.  They are three names for one
    real number, the one called $\sqrt2$.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. The digits are read off, not chosen

    Every nesting algorithm is equivalent to a **decimal** one.  The digits
    are produced greedily: having fixed $d_0.d_1\cdots d_{n-1}$, take the
    largest $d_n$ with

    $$(d_0.d_1\cdots d_n)_{10}\le b_k\quad\text{for every }k.$$

    Such a digit exists and is unique, so the rule is deterministic -- the
    expansion is a *consequence* of the algorithm.
    """)
    return


@app.cell
def _(mo):
    target = mo.ui.dropdown(
        options=["sqrt(2)", "sqrt(3)", "1/3", "1/2"],
        value="sqrt(2)",
        label="number",
    )
    places = mo.ui.slider(1, 12, value=8, label="digits")
    mo.hstack([target, places], justify="start", gap=2)
    return places, target


@app.cell
def _(Fraction, mo, places, target):
    _y = {"sqrt(2)": 2, "sqrt(3)": 3}.get(target.value)
    if _y is not None:
        def _below(t):
            return t * t < _y
        _start = Fraction(1)
    else:
        _r = Fraction(1, 3) if target.value == "1/3" else Fraction(1, 2)

        def _below(t):
            return t <= _r
        _start = Fraction(0)

    _t = _start
    while _below(_t + 1):
        _t += 1
    _rows = []
    for _k in range(1, places.value + 1):
        _u = Fraction(1, 10 ** _k)
        _d = 0
        while _d < 9 and _below(_t + _u * (_d + 1)):
            _d += 1
        _t += _u * _d
        _rows.append(rf"| {_k} | {_d} | ${float(_t):.{places.value}f}$ |")

    mo.md(rf"""
    | place | digit forced | truncation so far |
    |---|---|---|
    {chr(10).join(_rows)}

    At each place exactly one digit is admissible as the largest: nothing is
    chosen.  For $1/2$ the digits become $0$ forever -- the greedy rule
    produces $0.5000\ldots$, never $0.4999\ldots$, which is why the two
    expansions of a finite decimal need the equivalence to be identified.
    """)
    return


@app.cell
def _(mo, sys):
    mo.md(
        "---\n\n*Everything above is exact rational arithmetic "
        "(`fractions.Fraction`); no floating point enters the intervals.*"
        + (f"  Running under Python {sys.version.split()[0]}."
           if sys.platform != "emscripten" else "")
    )
    return


if __name__ == "__main__":
    app.run()
