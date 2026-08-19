"""Lecture 1, as a notebook the students can run in a browser.

    make numerics-edit NB=lec01     to write it
    make numerics                   to export it for the web

The arithmetic is not repeated here: every number still comes from
`numerics/analysis.py`, exactly as in `numerics/lec01_experiments.py`.  What
this file adds is the knob -- the reader picks the number and watches the
machine's answer change.
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

    import math
    from fractions import Fraction
    from decimal import Decimal, getcontext

    # `from matplotlib import pyplot`, not `import matplotlib.pyplot`: the
    # package scanner turns a dotted import into a dotted package name and
    # then asks PyPI for "matplotlib-pyplot", which does not exist.
    from matplotlib import pyplot as plt

    def sci(v, d=4):
        """A number in scientific notation, as LaTeX rather than as `1e-16`.

        Written into $...$, "2.2e-16" is read by the maths typesetter as an
        italic e minus 16.  This produces 2.2 \\times 10^{-16} instead.
        """
        if float(v) == 0.0:
            return "0"
        _mant, _exp = f"{float(v):.{d}e}".split("e")
        return rf"{_mant} \times 10^{{{int(_exp)}}}"

    _analysis = importlib.import_module("analysis")
    binary = _analysis.binary
    exact_decimal = _analysis.exact_decimal
    float_parts = _analysis.float_parts
    binary_float = _analysis.binary_float
    pow2_as_pow10 = _analysis.pow2_as_pow10
    spacing_at = _analysis.spacing_at
    babylonian = _analysis.babylonian
    return (
        Decimal,
        Fraction,
        binary,
        binary_float,
        exact_decimal,
        float_parts,
        getcontext,
        math,
        plt,
        pow2_as_pow10,
        sci,
        spacing_at,
        sys,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Lecture 1 — the numbers we manipulate

    The slides quote particular numbers. Here you can change them.

    Nothing is installed: this page carries its own Python and runs it in
    your browser. Every cell recomputes as soon as you move a control, so
    what you read is always the answer to the question currently on screen.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. A number under the microscope
    """)
    return


@app.cell
def _(mo):
    x_input = mo.ui.text(value="0.1", label="$x =$")
    digits = mo.ui.slider(8, 60, value=40, label="binary places shown")
    mo.vstack([x_input, digits])
    return digits, x_input


@app.cell
def _(binary, binary_float, digits, exact_decimal, float_parts, mo, x_input):
    try:
        x = float(x_input.value)
    except ValueError:
        x = None

    if x is None:
        _out = mo.md(f"**`{x_input.value}` is not a number.**")
    elif x == 0.0:
        _out = mo.md("**0 is stored exactly, and has no leading 1 to show.**")
    else:
        _s, _e, _m = float_parts(x)
        _out = mo.md(
            f"""
            | | |
            |---|---|
            | you asked for | `{x_input.value}` |
            | in base 2 | `{binary(x, digits.value)}...` |
            | what the machine holds, in base 2 | `{binary_float(x)}` |
            | the same, in base 10, exactly | `{exact_decimal(x)}` |
            | sign / exponent | `{_s}` / `{_e}` |

            The base-10 value in the fourth row is exact, not a rounded print:
            every float64 *is* a finite decimal. If it differs from what you
            typed, the number you asked for is not one the machine has.

            Try `0.5`, `0.25`, `3` — these stop. Then `0.1`, `0.2`, `1/3` as
            `0.3333333333` — these do not.
            """
        )
    _out
    return (x,)


@app.cell
def _(mo, sci, sys):
    mo.md(rf"""
    ## 2. Why there are only finitely many

    A float64 is 64 bits: 1 sign, 11 exponent, 52 mantissa. The 11
    exponent bits give $2^{{11}} = {2 ** 11}$ codes, of which 2 are
    reserved (zero and subnormals at one end, $\infty$ and NaN at the
    other), leaving ${2 ** 11 - 2}$ usable exponents,
    $-1022 \le e \le 1023$ — asymmetric by one code.

    $$2 \cdot 2046 \cdot 2^{{52}} = 2^{{64}} - 2^{{54}} = {sci(2 * 2046 * 2 ** 52)}$$

    | | |
    |---|---|
    | largest | ${sci(sys.float_info.max)}$ |
    | smallest positive normal | ${sci(sys.float_info.min)}$ |
    | $\varepsilon = 2^{{-52}}$ | ${sci(sys.float_info.epsilon)}$ |
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. The spacing is relative

    Between $2^e$ and $2^{e+1}$ the 52 mantissa bits divide an interval of
    length $2^e$ into $2^{52}$ equal parts, so the gap there is $2^{e-52}$:
    proportional to the size of the number. The machine's numbers are not
    spread evenly along the line — they crowd near zero and thin out as you
    move away, and the *relative* gap is the same everywhere.
    """)
    return


@app.cell
def _(math, mo, plt, spacing_at, x):
    _xs = [2.0 ** e for e in range(-40, 41)]
    _gaps = [spacing_at(v) for v in _xs]

    _fig, _ax = plt.subplots(figsize=(7, 3.6))
    _ax.loglog(_xs, _gaps, marker=".", linewidth=1)
    if x is not None and x > 0 and math.isfinite(x):
        _ax.loglog([x], [spacing_at(x)], marker="o", markersize=9,
                   fillstyle="none", color="crimson")
        _ax.annotate(f"your x = {x:g}", (x, spacing_at(x)),
                     textcoords="offset points", xytext=(8, -12),
                     color="crimson")
    _ax.set_xlabel("magnitude of the number")
    _ax.set_ylabel("gap to the next float64")
    _ax.grid(True, which="both", linewidth=0.3)
    _fig.tight_layout()
    mo.vstack([_fig, mo.md(
        "A straight line of slope 1 on log–log axes: the gap is a fixed "
        "*fraction* of the number, namely $2^{-52}$."
    )])
    return


@app.cell
def _(mo, sci, spacing_at):
    _rows = "\n".join(
        f"| ${sci(v)}$ | ${sci(spacing_at(v))}$ | ${sci(spacing_at(v) / v)}$ |"
        for v in (2.0 ** -20, 1.0, 2.0 ** 20)
    )
    mo.md(
        "| near | gap | gap / number |\n|---|---|---|\n" + _rows +
        "\n\nThe last column is $2^{-52}$ in every row."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Three experiments

    Each of these is a consequence of the spacing, not a bug.
    """)
    return


@app.cell
def _(mo, sys):
    _eps = sys.float_info.epsilon
    mo.md(
        f"""
        | | |
        |---|---|
        | `0.1 + 0.2 == 0.3` | `{0.1 + 0.2 == 0.3}` |
        | `0.1 + 0.2` | `{0.1 + 0.2!r}` |
        | `1 + eps/2 == 1` | `{1.0 + _eps / 2 == 1.0}` |
        | `1 + eps == 1` | `{1.0 + _eps == 1.0}` |

        The second is the first explained: `0.1` and `0.2` are each rounded on
        the way in, and the exact sum of what was stored is not what `0.3`
        rounds to. The third is the halfway case — `1 + eps/2` sits exactly
        between two machine numbers, and the tie is broken towards the one
        whose last bit is 0, which is 1 itself.
        """
    )
    return


@app.cell
def _(mo):
    big = mo.ui.slider(8, 20, value=16,
                       label="magnitude $k$ in $10^{k}$")
    big
    return (big,)


@app.cell
def _(big, mo):
    _a, _b, _c = 1.0, 10.0 ** big.value, -(10.0 ** big.value)
    mo.md(
        f"""
        Addition is not associative. With $b = 10^{{{big.value}}}$:

        | | |
        |---|---|
        | `(1 + b) + (-b)` | `{(_a + _b) + _c!r}` |
        | `1 + (b + (-b))` | `{_a + (_b + _c)!r}` |

        Move the slider down until the two agree: the 1 survives exactly as
        long as it is not smaller than the gap between machine numbers near
        $b$.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5. Ten binary places buy about three decimal ones

    Because $2^{10} = 1024$, a little more than $10^3$.
    """)
    return


@app.cell
def _(mo):
    n_bits = mo.ui.slider(1, 60, value=52, label="binary places $n$")
    n_bits
    return (n_bits,)


@app.cell
def _(math, mo, n_bits, pow2_as_pow10, sci):
    _r = pow2_as_pow10(n_bits.value)
    mo.md(
        rf"""
        $$2^{{-{n_bits.value}}} = {sci(_r["exact"], 6)}
          = 10^{{-{_r["k"]:.2f}}}$$

        Rule of thumb: $n = {n_bits.value}$ binary places
        $\approx 10^{{-{3 * _r["rule_of_thumb"]}}}$, against the true
        $10^{{-{_r["nearest_k"]}}}$.

        So the 52 bits of a float64 are worth about
        ${52 * math.log10(2):.1f}$ decimal digits — which is why printing 17
        digits of a float64 is the most that can ever mean anything.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6. The Babylonian iteration walks into the hole

    $b \mapsto \tfrac12\!\left(b + \tfrac{y}{b}\right)$, started at
    $b_0 = 2$. In exact fractions it never stops improving and never
    arrives: every $b_n$ is rational, every $b_n^2 > y$, and the limit is
    not rational. In float64 it stops moving after a handful of steps —
    not because it has arrived, but because it has run out of numbers.
    """)
    return


@app.cell
def _(mo):
    steps = mo.ui.slider(1, 8, value=5, label="steps")
    y_val = mo.ui.dropdown(options={"2": 2, "3": 3, "5": 5, "10": 10},
                           value="2", label="$y =$")
    mo.hstack([y_val, steps], justify="start", gap=2)
    return steps, y_val


@app.cell
def _(Decimal, Fraction, getcontext, mo, sci, steps, y_val):
    _y = y_val.value

    # The error is measured against a 60-digit square root, not against
    # math.sqrt: by step 5 the exact b_n already agrees with sqrt(y) to more
    # places than a float64 has, so a float subtraction would report 0 and
    # hide exactly the behaviour this table exists to show.
    getcontext().prec = 60
    _target = Decimal(_y).sqrt()

    _exact = Fraction(_y)
    _rows = []
    _f = float(_y)
    for _i in range(steps.value):
        _exact = (_exact + Fraction(_y) / _exact) / 2
        _f = (_f + _y / _f) / 2
        _rows.append(
            f"| {_i + 1} | `{_exact}` | "
            f"${sci(Decimal(_exact.numerator) / Decimal(_exact.denominator) - _target, 3)}$ | "
            f"`{_f!r}` |"
        )

    mo.md(
        f"""
        | $n$ | $b_n$ exactly | error | $b_n$ in float64 |
        |---|---|---|---|
        {chr(10).join(_rows)}

        The numerators and denominators double in length at every step: that
        growth is the price of staying exact. The float64 column pays a
        different price — it stops changing, and the last value it reaches is
        not $\\sqrt{{{_y}}}$ but the nearest machine number to it.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    Every function used above lives in `numerics/analysis.py`, the same
    file the slides compute from. Nothing on this page is transcribed.
    """)
    return


if __name__ == "__main__":
    app.run()
