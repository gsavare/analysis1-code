"""Two ideas trapping the same number, for lecture 2.

    python3 numerics/lec02_experiments.py

Digit-by-digit trapping (decimal, then binary -- where it becomes bisection)
and Newton read as an interval.  Each produces a nested family of rational
intervals with shrinking length, and they define the same real number.
"""

import sys, os
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def rule(t):
    print(f"\n{'=' * 74}\n{t}\n{'=' * 74}")


def show(n, lo, hi, extra=""):
    length = hi - lo
    print(f"  I_{n}  [{float(lo):.12f}, {float(hi):.12f}]   "
          f"length {float(length):.3e}  {extra}")


rule("1.  One digit at a time, base 10: try the candidates, square them")
print("  the digit kept is the largest whose square stays below 2.\n")
t = F(1)
for n in range(1, 4):
    step = F(1, 10 ** n)
    d = max(d for d in range(10) if (t + d * step) ** 2 < 2)
    for cand in (d, d + 1):
        s = (t + cand * step) ** 2
        mark = "keep" if cand == d else "too large"
        print(f"    candidate {float(t + cand*step):.{n}f}   "
              f"square {float(s):.6f}   {mark}")
    t += d * step
    print(f"  -> I_{n} = [{t}, {t + step}]\n")

rule("2.  One digit at a time, base 2: two candidates, one test = BISECTION")
print("  appending a binary digit tests the midpoint of the current interval.\n")
lo, hi = F(1), F(2)
digits = "1."
for n in range(1, 7):
    mid = (lo + hi) / 2
    if mid * mid > 2:
        hi = mid
        digits += "0"
    else:
        lo = mid
        digits += "1"
    show(n, lo, hi, f"digits so far ({digits})_2")
print(f"  exact endpoints of I_6: [{lo}, {hi}],  length {hi-lo}")

rule("3.  Newton / Babylon, read as an interval")
print("  if q^2 > 2 then 2/q < sqrt2 < q, so [2/q, q] traps it.")
q = F(2)
for n in range(1, 6):
    q = (q + 2 / q) / 2
    show(n, 2 / q, q)
print(f"  exact I_4 = [{2/q}, {q}]")

rule("4.  Do they meet?  The three families at step 4")
b_lo, b_hi = F(1), F(2)
for _ in range(4):
    m = (b_lo + b_hi) / 2
    if m * m > 2:
        b_hi = m
    else:
        b_lo = m
q = F(2)
for _ in range(4):
    q = (q + 2 / q) / 2
d = F("1.4142")
fams = {
    "bisection": (b_lo, b_hi),
    "Newton   ": (2 / q, q),
    "decimal  ": (d, d + F(1, 10 ** 4)),
}
for k, (a, b) in fams.items():
    print(f"  {k}  [{float(a):.10f}, {float(b):.10f}]")
lo = max(a for a, _ in fams.values())
hi = min(b for _, b in fams.values())
print(f"\n  common part: [{float(lo):.10f}, {float(hi):.10f}]  -> nonempty: {lo <= hi}")

rule("5.  A rational is a nesting algorithm too")
print("  the constant family I_n = [1/2, 1/2] traps 1/2 and nothing else.")
print("  so is I_n = [1/2 - 10^-n, 1/2 + 10^-n]: same number, different algorithm.")

rule("6.  Where the correspondence with expansions fails")
print("  1/2 has two expansions, 0.5000... and 0.4999..., hence two families:")
for n in range(1, 5):
    a = F(1, 2)
    print(f"    from 0.5000...  I_{n} = [{a}, {a + F(1,10**n)}]")
    t = F("0.4" + "9" * (n - 1)) if n > 1 else F("0.4")
    print(f"    from 0.4999...  I_{n} = [{t}, {t + F(1,10**n)}]")
print("\n  both shrink onto 1/2, and their intervals always meet:")
print("  same real number, two expansions.  This is the only way uniqueness fails.")
