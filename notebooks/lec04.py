"""Lecture 4, as a notebook the students can run in a browser.

    make numerics-edit NB=lec04     to write it
    make numerics                   to export it for the web

Three knobs, one per thing the slides can only assert:
  1. a recursion, run -- Newton, logistic, Collatz, the average of the last
     two terms: one real number per step, and no formula for it;
  2. the tolerance game -- choose epsilon, the notebook finds the first N
     from which the whole tail stays within epsilon of the limit, and draws
     the strip;
  3. the threshold game, the same for divergence.
The exact arithmetic of chapter 1 is not needed here: floating point is what
an algorithm actually runs on, and it is enough to watch the definition work.
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
    # page.  Kept identical to lec02.py on purpose: one setup, every notebook.
    import sys
    import os
    import importlib

    # `js`, `pyodide.http` and `analysis` are fetched through importlib rather
    # than with a plain `import`: in the browser marimo decides what to
    # install by reading the notebook's import statements, and all three
    # would be looked up on PyPI, not found, and take the real dependencies
    # down with them.  Kept dynamic, they are invisible to that scan.
    if sys.platform == "emscripten":
        js = importlib.import_module("js")
        pyodide_http = importlib.import_module("pyodide.http")
        _base = str(js.location.href).split("/assets/")[0].rstrip("/")
        _resp = await pyodide_http.pyfetch(f"{_base}/analysis.py")
        with open("analysis.py", "w") as _fh:
            _fh.write(await _resp.string())
        sys.path.insert(0, os.getcwd())
    else:
        sys.path.insert(0, str(mo.notebook_dir().parent))

    import math

    # `from matplotlib import pyplot`, not `import matplotlib.pyplot`: the
    # package scanner turns a dotted import into a dotted package name and
    # then asks PyPI for "matplotlib-pyplot", which does not exist.
    from matplotlib import pyplot as plt

    def dots(ax, xs, ys, **kw):
        """The sequence as points in the plane -- never joined: there is
        nothing between n and n+1."""
        ax.plot(xs, ys, "o", markersize=3.5, **kw)
        ax.set_xlabel("$n$")
        ax.spines[["top", "right"]].set_visible(False)

    return dots, math, plt, sys


@app.cell
def _(mo):
    mo.md(r"""
    # Sequences and algorithms

    An algorithm that never stops produces **one real number $a_n$ at each
    step**.  This notebook runs a few such algorithms, and simulates the
    definition of limit on the sequences whose limit is known.

    Nothing below is a proof.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. Recursions without an explicit formula

    Each rule is one line long.  Pick one, choose the starting value and how
    many steps to run, and look at the terms: the question *"does it settle,
    and where?"* has a different answer for each.
    """)
    return


@app.cell
def _(mo):
    rule = mo.ui.dropdown(
        options=[
            "Newton for sqrt(2):  a[n+1] = (a[n] + 2/a[n]) / 2",
            "logistic:  a[n+1] = 4 a[n] (1 - a[n])",
            "Collatz:  a[n+1] = a[n]/2  or  3 a[n] + 1",
            "average of the last two:  a[n+1] = (a[n] + a[n-1]) / 2",
            "geometric:  a[n+1] = q a[n]",
        ],
        value="Newton for sqrt(2):  a[n+1] = (a[n] + 2/a[n]) / 2",
        label="rule",
    )
    start = mo.ui.number(start=-100, stop=100, step=0.001, value=2.0,
                         label="$a_0$ (Collatz: rounded to a positive integer)")
    q = mo.ui.slider(-1.5, 1.5, step=0.05, value=0.8, label="$q$ (geometric only)")
    steps = mo.ui.slider(2, 60, value=15, label="steps")
    mo.vstack([rule, mo.hstack([start, q, steps], justify="start", gap=2)])
    return q, rule, start, steps


@app.cell
def _(dots, math, mo, plt, q, rule, start, steps):
    _name = rule.value.split(":")[0]
    _n = steps.value
    _a0 = float(start.value)

    if _name.startswith("Newton"):
        _x = _a0 if _a0 > 0 else 2.0
        _terms = [_x]
        for _ in range(_n):
            _x = 0.5 * (_x + 2.0 / _x)
            _terms.append(_x)
        _target, _note = math.sqrt(2), r"the terms approach $\sqrt2=1.41421356\ldots$"
    elif _name.startswith("logistic"):
        _x = _a0 if 0 < _a0 < 1 else 0.3
        _terms = [_x]
        for _ in range(_n):
            _x = 4.0 * _x * (1.0 - _x)
            _terms.append(_x)
        _target, _note = None, "no pattern: change $a_0$ in the sixth decimal and watch"
    elif _name.startswith("Collatz"):
        _x = max(1, int(round(_a0)))
        _terms = [_x]
        for _ in range(_n):
            _x = _x // 2 if _x % 2 == 0 else 3 * _x + 1
            _terms.append(_x)
        _target, _note = None, r"every start ever tried ends in the cycle $4,2,1$"
    elif _name.startswith("average"):
        _terms = [0.0, 1.0]
        for _ in range(_n - 1):
            _terms.append(0.5 * (_terms[-1] + _terms[-2]))
        _target, _note = 2 / 3, r"two steps of memory; the terms settle at $2/3$ (Exercise)"
    else:
        _terms = [1.0]
        for _ in range(_n):
            _terms.append(q.value * _terms[-1])
        _target = 0.0 if abs(q.value) < 1 else (1.0 if q.value == 1 else None)
        _note = r"$a_n=q^n$: the size of $q$ against $1$ decides everything"

    _fig, _ax = plt.subplots(figsize=(6.4, 2.6))
    dots(_ax, range(len(_terms)), _terms)
    if _target is not None:
        _ax.axhline(_target, color="tab:red", linewidth=0.8, linestyle="--")
    _ax.set_title(_name, fontsize=10)
    _fig.tight_layout()

    _shown = ", ".join(f"{_t:.6g}" for _t in _terms[:10])
    _tail = r", \ldots" if len(_terms) > 10 else ""
    mo.vstack([
        mo.md(rf"""
        First terms: ${_shown}{_tail}$

        *{_note}.*
        """),
        _fig,
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. The tolerance game

    The buyer picks a tolerance $\varepsilon$; the company must answer with
    an $N$ such that **every** term from $N$ on is within $\varepsilon$ of
    the limit.  Below, the notebook plays the company's move by brute force:
    it scans the terms and reports the first $N$ from which the tail never
    leaves the strip.  Compare it with the response the lecture computed by
    solving an inequality.
    """)
    return


@app.cell
def _(mo):
    seq = mo.ui.dropdown(
        options=["1/n", "n/(n+1)", "0.8^n", "(-1)^n"],
        value="1/n",
        label="sequence",
    )
    eps_exp = mo.ui.slider(1, 4, step=1, value=1, label=r"$\varepsilon=10^{-k}$, choose $k$")
    ell = mo.ui.slider(-1.5, 1.5, step=0.1, value=0.0,
                       label=r"candidate limit $\ell$ (used for $(-1)^n$ only)")
    mo.vstack([mo.hstack([seq, eps_exp], justify="start", gap=2), ell])
    return ell, eps_exp, seq


@app.cell
def _(dots, ell, eps_exp, mo, plt, seq):
    _eps = 10.0 ** (-eps_exp.value)
    _horizon = 20 * 10 ** eps_exp.value  # far enough to see the tail settle

    if seq.value == "1/n":
        _a, _l, _resp = (lambda n: 1.0 / n), 0.0, r"N=\lceil 1/\varepsilon\rceil"
        _first = 1
    elif seq.value == "n/(n+1)":
        _a, _l, _resp = (lambda n: n / (n + 1.0)), 1.0, r"N=\lceil 1/\varepsilon\rceil"
        _first = 0
    elif seq.value == "0.8^n":
        _a, _l, _resp = (lambda n: 0.8 ** n), 0.0, r"N=\lceil u/x\rceil \text{ with } 1/0.8=1+x"
        _first = 0
    else:
        _a, _l, _resp = (lambda n: (-1.0) ** n), float(ell.value), r"\text{none: the game is lost at } \varepsilon=1/2"
        _first = 0

    # the company's move, by brute force: the last index OUTSIDE the strip,
    # plus one -- the tail from there on is inside
    _last_out = None
    for _n in range(_first, _horizon + 1):
        if abs(_a(_n) - _l) > _eps:
            _last_out = _n
    _N = _first if _last_out is None else _last_out + 1
    _lost = _N > _horizon

    _fig, _ax = plt.subplots(figsize=(6.4, 2.6))
    _show = min(_horizon, max(30, 3 * _N if not _lost else 30))
    _ns = list(range(_first, _show + 1))
    _ax.axhspan(_l - _eps, _l + _eps, color="tab:red", alpha=0.12)
    _ax.axhline(_l, color="tab:red", linewidth=0.8)
    dots(_ax, _ns, [_a(_n) for _n in _ns])
    if not _lost:
        _ax.axvline(_N, color="gray", linestyle="--", linewidth=0.8)
    _ax.set_title(rf"${seq.value}$,  $\varepsilon=10^{{-{eps_exp.value}}}$", fontsize=10)
    _fig.tight_layout()

    _verdict = (
        rf"no $N$ up to ${_horizon}$ works: the strip of half-width "
        rf"${_eps:g}$ around $\ell={_l:g}$ never holds the whole tail"
        if _lost else
        rf"first $N$ from which the whole tail is within $\varepsilon$: "
        rf"$N={_N}$ (checked up to $n={_horizon}$)"
    )
    mo.vstack([
        mo.md(rf"""
        {_verdict}.

        The lecture's response, by solving the inequality: ${_resp}$.  It
        need not be the sharpest: any response wins the round.
        """),
        _fig,
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. The threshold game

    Divergence to $+\infty$ is the same game with a **threshold** in place
    of a tolerance: the buyer names $u$, and the tail must live above it.
    """)
    return


@app.cell
def _(mo):
    dseq = mo.ui.dropdown(
        options=["n", "n^2", "1.1^n", "n!"],
        value="1.1^n",
        label="sequence",
    )
    thr = mo.ui.slider(1, 6, step=1, value=3, label=r"$u=10^{k}$, choose $k$")
    mo.hstack([dseq, thr], justify="start", gap=2)
    return dseq, thr


@app.cell
def _(dseq, math, mo, thr):
    _u = 10.0 ** thr.value
    _a = {
        "n": (lambda n: float(n)),
        "n^2": (lambda n: float(n) ** 2),
        "1.1^n": (lambda n: 1.1 ** n),
        "n!": (lambda n: float(math.factorial(n))),
    }[dseq.value]
    _resp = {
        "n": r"N=\lceil u\rceil",
        "n^2": r"N=\lceil \sqrt u\,\rceil",
        "1.1^n": r"N=\lceil u/0.1\rceil \text{ (Bernoulli)}",
        "n!": r"N=\lceil u\rceil \text{ (since } n!\ge n)",
    }[dseq.value]

    # all four are increasing, so the first index above u is the response
    _n = 0
    while _a(_n) < _u:
        _n += 1

    mo.md(rf"""
    ${dseq.value}\ge{_u:g}$ from $n={_n}$ on.

    The lecture's response: ${_resp}$.  For $1.1^n$ Bernoulli's bound is
    much larger than the first index above $u$, and it is still a valid
    response: the definition asks for some $N$, not for the smallest.
    """)
    return


@app.cell
def _(mo, sys):
    mo.md(
        "---\n\n*Floating point throughout: this is what an algorithm runs on. "
        "Chapter 1's exact rationals live in the lec02 notebook.*"
        + (f"  Running under Python {sys.version.split()[0]}."
           if sys.platform != "emscripten" else "")
    )
    return


if __name__ == "__main__":
    app.run()
