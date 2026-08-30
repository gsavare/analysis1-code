"""Every number quoted in lecture 1, computed rather than transcribed.

    python3 numerics/lec01_experiments.py

Run this in class: the students can run it too, and it takes no setup.
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fractions import Fraction

from analysis import (binary, exact_decimal, float_parts, binary_float,
                 pow2_as_pow10, spacing_at, digits_of, repeating_block,
                 rounding_error, babylonian)


def rule(title):
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


rule("1.  One tenth, in base 10 and in base 2")
print(f"  0.1 in base 10 :  0.1                     (two digits, and it stops)")
print(f"  0.1 in base  2 :  {binary(0.1, 40)}...")
print(f"                    that is (0.0[0011][0011]...)_2, and it never stops")
print(f"\n  so the machine cannot hold 0.1.  What it holds instead is")
print(f"  in base  2 :  {binary_float(0.1)}")
print(f"  in base 10 :  {exact_decimal(0.1)}")

rule("2.  What a float64 is")
for x in (1.0, 0.1, 2.0):
    s, e, m = float_parts(x)
    print(f"  {x:<6} sign={s}  exponent={e:<5} mantissa={m[:20]}...")
print("\n  the 64 bits: 1 sign + 11 exponent + 52 mantissa.")
print(f"  11 bits give {2**11} codes; 2 are reserved (0/subnormals, inf/NaN),")
print(f"  leaving {2**11 - 2} exponents: -1022 <= e <= 1023  (asymmetric by one code).")
n_float = 2 * 2046 * 2**52
print(f"\n  how many there are   : 2*2046*2^52 = 2^64 - 2^54")
print(f"                       = {n_float} = {n_float:.4e}")
print(f"  check 2^64 - 2^54    : {2**64 - 2**54 == n_float}")
print(f"  largest              : {sys.float_info.max:e}")
print(f"  smallest positive    : {sys.float_info.min:e}")
print(f"  eps = 2^-52          : {sys.float_info.epsilon:e}")

rule("3.  The spacing is relative: the gap scales with the number")
print(f"  {'near':>12} {'gap':>14} {'gap / number':>16}")
for x in (2.0**-20, 1.0, 2.0**20):
    g = spacing_at(x)
    print(f"  {x:>12.4e} {g:>14.4e} {g / x:>16.4e}")
print(f"\n  the relative gap is 2^-52 = {2.0**-52:.4e} in every case:")
print("  between 2^e and 2^(e+1) the 52 digits cover a length 2^e, so the")
print("  gap is 2^(e-52) -- proportional to the size of the number.")
print(f"\n  landmarks used on the slide: 2^20 = {2**20} ~ 10^6, gap 2^-32 = {2.0**-32:.4e}")
print(f"                               2^-20 = {2.0**-20:.4e} ~ 10^-6, gap 2^-72 = {2.0**-72:.4e}")

rule("3b.  Rounding, and the halfway case")
print("  fl(x) is the nearest machine number; ties go to the one with b52 = 0.")
half = 1.0 + 2.0**-53          # exactly halfway between 1 and 1 + eps
print(f"  1 + eps/2 is exactly halfway between 1 and 1 + eps:")
print(f"    fl(1 + eps/2) = {half!r}   -> rounded down to 1 (its last bit is 0)")
print(f"    fl(1 + 3*eps/2) = {1.0 + 3 * 2.0**-53!r}  -> rounded up (1 + eps has last bit 0)")

rule("4.  Two experiments")
print(f"  0.1 + 0.2 == 0.3      ->  {0.1 + 0.2 == 0.3}")
print(f"  0.1 + 0.2             ->  {0.1 + 0.2!r}")
eps = sys.float_info.epsilon
print(f"  1 + eps/2 == 1        ->  {1.0 + eps / 2 == 1.0}")
print(f"  1 + eps   == 1        ->  {1.0 + eps == 1.0}")
a, b, c = 1.0, 1e16, -1e16
print(f"\n  addition is not even associative:")
print(f"  (1 + 1e16) + (-1e16)  ->  {(a + b) + c!r}")
print(f"  1 + (1e16 + (-1e16))  ->  {a + (b + c)!r}")

rule("5.  Converting between the two bases (float64 digits, and the exercises)")
print(f"  {'n':>4} {'2^-n':>26} {'= 10^-k, k =':>14} {'rule of thumb':>16}")
for n in (10, 20, 52, 53):
    r = pow2_as_pow10(n)
    print(f"  {r['n']:>4} {float(r['exact']):>26.3e} {r['k']:>14.2f} "
          f"{'10^-' + str(3 * r['rule_of_thumb']):>16}")
print(f"\n  because 2^10 = {2**10} = a little more than 10^3.")
print(f"  So the 52 bits of a float64 are worth about {52 * math.log10(2):.1f} decimal digits.")

rule("5b.  Reading the digits off a number")
print("  d_k = floor(b x_{k-1}),  x_k = b x_{k-1} - d_k,  in exact fractions.")
print("  the state x_k decides everything: 0 means it stops, a repeat means a cycle.\n")
for num, den, base in ((1, 2, 2), (1, 10, 2), (1, 5, 2), (1, 3, 10), (5, 16, 2)):
    x = Fraction(num, den)
    prefix, block = repeating_block(x, base)
    pre = "".join(map(str, prefix))
    if block:
        shown = f"0.{pre}[{''.join(map(str, block))}] repeating"
    else:
        shown = f"0.{pre} terminates"
    print(f"    {num}/{den:<3} in base {base:<3} -> {shown}")

print("\n  the first few steps for 1/10 in base 2, state and all:")
for k, d, state in digits_of(Fraction(1, 10), 2, 9):
    print(f"    k={k}  d_k={d}   x_k = {state}")
print("  x_5 = x_1, so the block 0011 repeats from there -- as on the slide.")

rule("5c.  eps is a RELATIVE bound: |fl(x) - x| / |x| <= eps/2")
print(f"  eps/2 = 2^-53 = {2.0**-53:.4e}\n")
print(f"    {'x':>14}   {'absolute error':>16}   {'relative error':>16}   ok?")
for num, den in ((1, 10), (1, 3), (2, 3), (10**6, 3), (1, 10**6 * 3)):
    x = Fraction(num, den)
    e = rounding_error(x)
    ok = e["relative"] <= 2.0**-53
    print(f"    {float(x):>14.4e}   {e['absolute']:>16.4e}   "
          f"{e['relative']:>16.4e}   {ok}")
print("\n  the absolute error moves by twelve orders of magnitude; the relative")
print("  one never crosses eps/2.  That is why the slide bounds the relative one.")

rule("6.  The Babylonian iteration walks into the hole")
print("  b -> (b + 2/b)/2, started at b0 = 2, in exact fractions:")
from fractions import Fraction
b = Fraction(2)
for i in range(4):
    b = (b + Fraction(2) / b) / 2
    err = float(b) - math.sqrt(2)
    print(f"    b{i+1} = {str(b):<25} = {float(b):.15f}   error {err:.2e}")
print("\n  every b is rational, every b squared is > 2, and the limit is not rational.")
print("  in float64 the same iteration stops moving after 5 steps:")
b = 2.0
for i in range(6):
    b = (b + 2 / b) / 2
    print(f"    b{i+1} = {b!r}")
