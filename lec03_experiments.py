"""The separation theorem by bisection, for lecture 3.

    python3 numerics/lec03_experiments.py

The point of the lecture, made computationally: the bisection that PROVES the
cut of lecture 1 has a separator is the same algorithm that DEFINED sqrt2 in
lecture 2.  Run both and compare the intervals.
"""

import sys, os
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def rule(t):
    print(f"\n{'=' * 74}\n{t}\n{'=' * 74}")


def separation_bisection(is_upper_bound_of_A, a, b, steps):
    """Bisect [a, b], keeping a NOT an upper bound of A and b AN upper bound."""
    out = []
    for _ in range(steps):
        m = (a + b) / 2
        if is_upper_bound_of_A(m):
            b = m
        else:
            a = m
        out.append((a, b))
    return out


rule("1.  The cut of lecture 1:  A = { p > 0 : p^2 < 2 },  B = { q > 0 : q^2 > 2 }")
print("  invariant: a is never an upper bound of A, b always is.")
print("  for m > 0, 'm is an upper bound of A' is the same test as 'm^2 >= 2'.\n")
sep_steps = separation_bisection(lambda m: m * m >= 2, F(1), F(2), 6)
for n, (a, b) in enumerate(sep_steps, 1):
    print(f"  n={n}  a={str(a):<9} b={str(b):<9} "
          f"length {str(b-a):<7} [{float(a):.6f}, {float(b):.6f}]")

rule("2.  The bisection that DEFINED sqrt2 in lecture 2")
lo, hi = F(1), F(2)
def_steps = []
for _ in range(6):
    m = (lo + hi) / 2
    if m * m > 2:
        hi = m
    else:
        lo = m
    def_steps.append((lo, hi))
for n, (a, b) in enumerate(def_steps, 1):
    print(f"  n={n}  a={str(a):<9} b={str(b):<9} "
          f"length {str(b-a):<7} [{float(a):.6f}, {float(b):.6f}]")

rule("3.  Are they the same algorithm?")
same = sep_steps == def_steps
print(f"  identical at every step: {same}")
print("\n  They are.  'm is an upper bound of A' and 'm^2 >= 2' are the same")
print("  test, so separating the cut and constructing sqrt2 are one act.")

rule("4.  The separator, and the supremum it hands us for free")
a, b = sep_steps[-1]
print("  the separator sigma satisfies p <= sigma <= q for p in A, q in B,")
print(f"  and after 6 steps it is trapped in [{float(a):.6f}, {float(b):.6f}].")
print("  sigma is also sup A = min of the upper bounds of A: the separator")
print("  between S and the set U of its upper bounds is what sup S means.")

rule("5.  Archimedes, and rationals below any positive real")
print("  a real x > 0 means: some interval [a_n, b_n] of x has a_n > 0.")
print("  then a_n is a positive rational with a_n <= x, and a_n/2 < x.")
print("  nothing to prove beyond reading the definition of the order.\n")
x = def_steps[-1]
print(f"  e.g. sqrt2 has I_6 = [{x[0]}, {x[1]}], so {x[0]}/2 = {x[0]/2} < sqrt2.")

rule("6.  sup without max: S = { 1 - 1/n : n >= 1 }")
print("  upper bound 1; and 2' holds: 1 - 1/n > 1 - eps as soon as 1/n < eps.")
for eps in (F(1, 10), F(1, 100), F(1, 1000)):
    n = int(1 / eps) + 1
    print(f"    eps = {str(eps):<7} ->  n = {n:<5}  1 - 1/n = {float(1 - F(1, n)):.6f} > {float(1-eps):.6f}")
print("  so sup S = 1, and it is not a maximum: 1 is not of the form 1 - 1/n.")
