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
    digits_of = _analysis.digits_of
    repeating_block = _analysis.repeating_block
    rounding_error = _analysis.rounding_error
    babylonian = _analysis.babylonian
    return (
        Decimal,
        Fraction,
        binary,
        binary_float,
        digits_of,
        exact_decimal,
        float_parts,
        getcontext,
        math,
        plt,
        pow2_as_pow10,
        repeating_block,
        rounding_error,
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
def _(mo):
    window = mo.ui.dropdown(
        options={"around 1": 0, "around 2": 1, "around 1/2": -1,
                 "around 8": 3, "around 1/8": -3},
        value="around 1",
        label="window",
    )
    window
    return (window,)


@app.cell
def _(mo, plt, sci, window):
    # ONE axis, in absolute units, spanning 2^e to a little past 2^(e+1).  Two
    # panels would defeat the purpose: drawn side by side each to its own
    # width, the ticks come out equally spaced and the doubling -- the whole
    # content of the picture -- becomes invisible.  Here both runs of numbers
    # sit on the same line at their true distances, so the gap on the right is
    # visibly twice the gap on the left.
    _e = int(window.value)
    _lo = 2.0 ** _e                      # the power of two we straddle
    _gap = 2.0 ** (_e - 52)              # spacing just below it, and above
    _n = 7

    # Consecutive machine numbers on each side of 2^(e+1), where the gap
    # doubles.  Expressed in units of the small gap so the axis is readable:
    # the left run steps by 1, the right run by 2.
    _left = [(-_k) for _k in range(_n)][::-1]        # ..., -2, -1, 0
    _right = [2 * _k for _k in range(1, _n + 1)]     # 2, 4, 6, ...

    _fig, _ax = plt.subplots(figsize=(7.4, 2.4))
    _ax.plot(_left, [0] * len(_left), marker="|", markersize=22,
             linestyle="none", color="black")
    _ax.plot(_right, [0] * len(_right), marker="|", markersize=22,
             linestyle="none", color="black")
    # The dashed line stops short of the label below it, which it otherwise
    # strikes through.
    _ax.axvline(0, ymin=0.30, ymax=0.95, color="crimson", linewidth=1.1,
                linestyle="--", alpha=0.8)

    # The two spacings, measured on the picture itself.
    _ax.annotate("", xy=(-2, 0.45), xytext=(-1, 0.45),
                 arrowprops=dict(arrowstyle="<->", color="black", lw=1))
    _ax.text(-1.5, 0.62, f"${sci(_gap, 2)}$", ha="center", fontsize=9)
    _ax.annotate("", xy=(2, 0.45), xytext=(4, 0.45),
                 arrowprops=dict(arrowstyle="<->", color="crimson", lw=1))
    _ax.text(3, 0.62, f"${sci(2 * _gap, 2)}$", ha="center",
             fontsize=9, color="crimson")

    _ax.text(0, -0.82, f"$2^{{{_e + 1}}} = {2 * _lo:g}$", ha="center",
             fontsize=10, color="crimson")
    _ax.set_xlim(-_n - 0.5, 2 * _n + 1.5)
    _ax.set_ylim(-1.1, 1.1)
    _ax.set_yticks([])
    _ax.set_xticks([])
    for _sp in ("left", "right", "top"):
        _ax.spines[_sp].set_visible(False)
    _ax.spines["bottom"].set_position(("data", 0))
    _fig.tight_layout()

    mo.vstack([_fig, mo.md(
        f"""
        Consecutive `float64` on both sides of $2^{{{_e + 1}}}$, at their true
        distances on one line. Below the mark they are ${sci(_gap, 2)}$ apart;
        above it, ${sci(2 * _gap, 2)}$ — **twice as far**. Crossing a power of
        two, the machine spends the same 52 digits on an interval twice as
        long, so the numbers thin out by a factor of 2 and stay that way until
        the next power.

        Change the window and both numbers scale with it: halve the
        magnitude and both gaps halve. Only their *ratio* to the number they
        sit near never moves, and that ratio is $2^{{-52}}$.
        """
    )])
    return


@app.cell
def _(math, mo, plt, spacing_at, x):
    # The global view, for contrast.  Over eighty orders of magnitude the gap
    # is a straight line of slope 1 -- true, but a log-log plot cannot show
    # what a gap looks like.  The window above is what the numbers do.
    _xs = [2.0 ** e for e in range(-40, 41)]
    _gaps = [spacing_at(v) for v in _xs]

    _fig, _ax = plt.subplots(figsize=(7, 2.8))
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
        "The same fact over the whole range: a straight line of slope 1, "
        "i.e. the gap is a fixed *fraction* of the number, namely $2^{-52}$."
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
def _(mo):
    a_in = mo.ui.text(value="0.1", label="$a =$")
    b_in = mo.ui.text(value="0.2", label="$b =$")
    c_in = mo.ui.text(value="0.3", label="compare with $c =$")
    mo.hstack([a_in, b_in, c_in], justify="start", gap=1)
    return a_in, b_in, c_in


@app.cell
def _(Fraction, a_in, b_in, c_in, mo, sci, sys):
    _eps = sys.float_info.epsilon
    try:
        _a, _b, _c = (float(a_in.value), float(b_in.value), float(c_in.value))
    except ValueError:
        _out = mo.md("**Those are not all numbers.**")
    else:
        # Why a+b differs from c: compare the exact sum of what was *stored*
        # with what c rounds to.  Fraction(float) is exact, so this is the
        # real reason and not a restatement of the symptom.
        _exact_sum = Fraction(_a) + Fraction(_b)
        _stored_sum = Fraction(_a + _b)
        _stored_c = Fraction(_c)
        _same = (_a + _b) == _c

        _out = mo.md(
            f"""
            | | |
            |---|---|
            | `{_a!r} + {_b!r} == {_c!r}` | `{_same}` |
            | `{_a!r} + {_b!r}` | `{_a + _b!r}` |
            | exact sum of what was stored | ${sci(float(_exact_sum), 6)}$ |
            | what `{_c!r}` stores | ${sci(float(_stored_c), 6)}$ |
            | difference | ${sci(float(_stored_sum - _stored_c), 3)}$ |

            `{_a!r}` and `{_b!r}` are each rounded on the way in, and the exact
            sum of what was stored is {"" if _same else "not "}what `{_c!r}`
            rounds to.

            Try `0.5`, `0.25`, `0.125` — sums of numbers the machine holds
            exactly come out exactly right. The trouble is never the addition;
            it is what happened before it.
            """
        )
    _out
    return


@app.cell
def _(mo, sys):
    _eps = sys.float_info.epsilon
    mo.md(
        f"""
        The halfway case, which needs no knob — it is about $1$ itself:

        | | |
        |---|---|
        | `1 + eps/2 == 1` | `{1.0 + _eps / 2 == 1.0}` |
        | `1 + eps == 1` | `{1.0 + _eps == 1.0}` |

        `1 + eps/2` sits exactly between two machine numbers, and the tie is
        broken towards the one whose last bit is $0$ — which is $1$ itself.
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
    ## 5. Converting between the two bases

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

    # The error is measured against a high-precision square root, not against
    # math.sqrt: by step 5 the exact b_n already agrees with sqrt(y) to more
    # places than a float64 has, so a float subtraction would report 0 and
    # hide exactly the behaviour this table exists to show.  The precision has
    # to outrun the iteration, which doubles its correct digits every step --
    # at 60 digits the error prints as 0 from n = 7 on, which is the same lie
    # in slower motion.
    getcontext().prec = max(60, 8 * 2 ** steps.value)
    _target = Decimal(_y).sqrt()

    def _short(frac, keep=11):
        """The fraction, with the middle elided once it stops fitting.

        The digits double in length at every step -- by n = 6 the numerator
        alone is 25 digits -- so printing them in full breaks the table.  The
        length is what matters here, and it is reported instead.

        No raw HTML: <br> and <small> survive marimo's local renderer but are
        dropped by the exported site, which is where this table is actually
        read.  Plain markdown says the same thing and travels.
        """
        _n, _d = str(frac.numerator), str(frac.denominator)
        if len(_n) <= keep:
            return f"`{_n}/{_d}`"
        return (f"`{_n[:4]}…{_n[-3:]}`/`{_d[:4]}…{_d[-3:]}` "
                f"({len(_n)} and {len(_d)} digits)")

    _exact = Fraction(_y)
    _rows = []
    _f = float(_y)
    for _i in range(steps.value):
        _exact = (_exact + Fraction(_y) / _exact) / 2
        _f = (_f + _y / _f) / 2
        _err = Decimal(_exact.numerator) / Decimal(_exact.denominator) - _target
        _rows.append(
            f"| {_i + 1} | {_short(_exact)} | ${sci(_err, 3)}$ | `{_f!r}` |"
        )

    # Flat string, zero indentation -- see the note in section 7: rows
    # interpolated into an indented block break the table after the first one.
    _table = "\n".join(
        ["| $n$ | $b_n$ exactly | error | $b_n$ in float64 |",
         "|---|---|---|---|"] + _rows
    )
    mo.md(
        _table
        + "\n\n"
        + "The numerator and denominator **double in length at every step** — "
          "that growth is the price of staying exact, and it is why the middle "
          "of the fraction is elided above rather than printed. The float64 "
          "column pays a different price: it stops changing, and the value it "
          rf"settles on is not $\sqrt{{{_y}}}$ but the nearest machine "
          "number to it."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 7. Reading the digits off a number

    Multiply by the base, record the integer part, keep the rest. The digits
    come out one at a time, and the **state** — the part you keep — decides
    what happens: reach $0$ and the expansion stops, meet a state you have
    already seen and everything repeats from there.

    Pick a fraction and a base, and watch the states.
    """)
    return


@app.cell
def _(mo):
    num = mo.ui.number(1, 999, value=1, label="numerator")
    den = mo.ui.number(1, 999, value=10, label="denominator")
    base = mo.ui.dropdown(["2", "3", "10", "16"], value="2", label="base")
    mo.vstack([mo.hstack([num, den]), base])
    return base, den, num


@app.cell
def _(Fraction, base, den, digits_of, mo, num, repeating_block):
    _b = int(base.value)
    _x = Fraction(int(num.value), int(den.value))

    if not 0 <= _x < 1:
        _out = mo.md("**Pick a fraction in $[0,1)$** — the algorithm reads "
                     "digits after the point.")
    else:
        _prefix, _block = repeating_block(_x, _b)
        _pre = "".join(str(_d) for _d in _prefix)
        if _block == []:
            _verdict = (f"terminates: $({{0.{_pre}}})_{{{_b}}}$ — the state "
                        f"reached $0$.")
        elif _block:
            _blk = "".join(str(_d) for _d in _block)
            _verdict = (f"repeats: $({{0.{_pre}}}\\overline{{{_blk}}})_{{{_b}}}$ "
                        f"— block of length {len(_block)}.")
        else:
            _verdict = "no cycle found within the places computed."

        # The table is assembled at zero indentation and handed to mo.md as
        # one flat string.  Interpolating rows into an indented triple-quoted
        # block indents the FIRST row only -- the rest arrive at column 0, the
        # dedent no longer matches, and the table breaks apart after row one.
        _rows = [f"| {_k} | {_d} | ${_st.numerator}/{_st.denominator}$ |"
                 for _k, _d, _st in digits_of(_x, _b, 12)]
        _table = "\n".join(
            [f"$x = {_x.numerator}/{_x.denominator}$ in base ${_b}$ {_verdict}",
             "",
             "| $k$ | $d_k$ | state $x_k$ |",
             "|---|---|---|"] + _rows
        )
        _out = mo.md(
            _table
            + "\n\n"
            + "A rational must do one or the other: the state is always a "
              "fraction with the same denominator, so there are finitely many "
              "of them and one has to come back."
        )
    _out
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 8. Why $\varepsilon_{\mathrm{mach}}$ is a *relative* bound

    The slide claims $|\mathrm{fl}(x)-x|/|x| \le \varepsilon/2$, and says the
    absolute error has no useful bound at all. Move $x$ across the orders of
    magnitude and watch which of the two columns stays put.
    """)
    return


@app.cell
def _(mo):
    scale = mo.ui.slider(-12, 12, value=0,
                         label="$x = 1/3 \\times 10^{k}$, $k =$")
    scale
    return (scale,)


@app.cell
def _(Fraction, mo, rounding_error, scale, sci):
    _k = int(scale.value)
    _x = Fraction(1, 3) * Fraction(10) ** _k
    _e = rounding_error(_x)
    _bound = 2.0 ** -53
    _ok = "yes" if _e["relative"] <= _bound else "**no**"

    # rf, not f: \varepsilon in a plain f-string is \v + "arepsilon", i.e. a
    # vertical tab.  It shows up as a broken symbol only in the exported site,
    # where the code is hidden and the output is all there is.
    _table = "\n".join([
        "| | value |",
        "|---|---|",
        rf"| $x$ | ${sci(float(_x))}$ |",
        rf"| absolute error $\lvert\mathrm{{fl}}(x)-x\rvert$ | ${sci(_e['absolute'])}$ |",
        rf"| relative error | ${sci(_e['relative'])}$ |",
        rf"| within $\varepsilon/2 = {sci(_bound, 2)}$? | {_ok} |",
    ])
    mo.md(
        _table
        + "\n\n"
        + "The absolute error follows the number over twenty-four orders of "
          "magnitude; the relative one does not move. That is the whole reason "
          "the error worth quoting is the relative one — and the reason a "
          "single constant can describe the precision everywhere."
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
