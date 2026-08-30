"""Small numerical toolbox for the BAI Analysis course.

Everything the slides claim about numbers is computed here, so that the text
and the arithmetic cannot drift apart.  Pure standard library: no install, no
environment to maintain, runs with any python3.

    from analysis import *
    binary(0.1, 40)          -> '0.0001100110011001100110011001100110011001'
    exact_decimal(0.1)       -> Decimal('0.1000000000000000055511151231257827021181583404541015625')
    float_parts(0.1)         -> sign, exponent, 52 mantissa bits
    binary_float(0.1)        -> '(1.1001...1010)_2 x 2^-4'

Run it directly to reproduce every number quoted in lecture 1:

    python3 numerics/lec01_experiments.py
"""

from decimal import Decimal, getcontext
from fractions import Fraction
import math
import struct

__all__ = [
    "binary", "decimal_digits", "exact_decimal", "float_parts", "binary_float",
    "pow2_as_pow10", "spacing_at", "digits_of", "repeating_block",
    "rounding_error", "bisect",
    "babylonian",
]


# ---------------------------------------------------------------------------
# Writing a number in a base
# ---------------------------------------------------------------------------

def binary(x, digits=52):
    """The base-2 expansion of x, as a string, truncated to `digits` places.

    Uses exact rational arithmetic on the float, so what comes out is what the
    machine really holds -- not a rounded decimal print of it.
    """
    if x < 0:
        return "-" + binary(-x, digits)
    whole = int(x)
    frac = Decimal(x) - Decimal(whole)   # Decimal(float) is exact
    out = [bin(whole)[2:] if whole else "0", "."]
    for _ in range(digits):
        frac *= 2
        bit = int(frac)
        out.append(str(bit))
        frac -= bit
        if frac == 0:
            break
    return "".join(out)


def decimal_digits(x, digits=25):
    """The base-10 expansion of x, exact, truncated to `digits` places."""
    getcontext().prec = digits + 30
    return str(Decimal(x).quantize(Decimal(1).scaleb(-digits)))


def exact_decimal(x):
    """The exact value of the float x, which is always a finite decimal."""
    return Decimal(x)


# ---------------------------------------------------------------------------
# What a float64 actually is
# ---------------------------------------------------------------------------

def float_parts(x):
    """(sign, exponent, mantissa_bits) of the float64 x, as on the slide.

    x = (-1)^sign * (1.mantissa_bits)_2 * 2^exponent   for normal numbers.
    """
    bits = struct.unpack(">Q", struct.pack(">d", x))[0]
    sign = bits >> 63
    biased = (bits >> 52) & 0x7FF
    mantissa = bits & ((1 << 52) - 1)
    exponent = biased - 1023
    return sign, exponent, format(mantissa, "052b")


def binary_float(x):
    """x written the way the hardware stores it: (1.b1...b52)_2 * 2^e."""
    sign, exponent, mantissa = float_parts(x)
    return f"{'-' if sign else ''}(1.{mantissa})_2 x 2^{exponent}"


def spacing_at(x):
    """Distance from x to the next float64 above it."""
    return math.nextafter(x, math.inf) - x


# ---------------------------------------------------------------------------
# Moving between powers of 2 and powers of 10
# ---------------------------------------------------------------------------

def pow2_as_pow10(n):
    """Report 2^-n as a power of 10: the exact value and the nearest 10^-k.

    The bridge worth remembering is 2^10 = 1024, a little more than 10^3, so
    ten binary places buy about three decimal ones.
    """
    exact = Decimal(2) ** -n
    k = n * math.log10(2)
    return {
        "n": n,
        "exact": exact,
        "k": k,                       # 2^-n = 10^-k
        "nearest_k": round(k),
        "rule_of_thumb": n // 10,     # 2^-n ~ 10^-3(n/10)
    }


# ---------------------------------------------------------------------------
# Reading the digits off a number
# ---------------------------------------------------------------------------

def digits_of(x, base=10, places=12):
    """The base-`base` digits of x in [0, 1), by the algorithm of the slide.

    Multiply by the base, record the integer part, keep the rest:

        x_0 = x,   d_k = floor(b x_{k-1}),   x_k = b x_{k-1} - d_k.

    Exact rational arithmetic throughout, so the state x_k is the true one and
    a repeating block really repeats.  Yields (k, d_k, x_k); stops early if the
    state reaches 0, i.e. if the expansion terminates.
    """
    x = Fraction(x)
    if not 0 <= x < 1:
        raise ValueError("digits_of expects x in [0, 1)")
    for k in range(1, places + 1):
        shifted = base * x
        d = int(shifted)              # floor, since shifted >= 0
        x = shifted - d
        yield k, d, x
        if x == 0:
            return


def repeating_block(x, base=10, places=60):
    """The digits of x in the given base, marking where the state repeats.

    Returns (prefix, block): the digits before the cycle and the cycle itself,
    with block empty when the expansion terminates.  A rational always does one
    or the other -- there are finitely many possible states.
    """
    seen, digs = {}, []
    x = Fraction(x)
    for k, d, state in digits_of(x, base, places):
        digs.append(d)
        if state == 0:
            return digs, []
        if state in seen:
            start = seen[state]
            return digs[:start], digs[start:]
        seen[state] = k
    return digs, None                 # no cycle found within `places`


def rounding_error(x):
    """How far fl(x) is from x, absolutely and relative to x.

    The relative error is what the slide bounds by eps/2 = 2^-53; the absolute
    one has no useful bound at all, and that is the point.
    """
    fl = float(x)
    exact = Fraction(x)
    err = abs(Fraction(fl) - exact)
    return {
        "absolute": float(err),
        "relative": float(err / abs(exact)) if exact else 0.0,
    }


# ---------------------------------------------------------------------------
# The two algorithms of lecture 1
# ---------------------------------------------------------------------------

def bisect(f, a, b, steps):
    """Binary search for a zero of f in [a, b].  Yields (a, b) at each step."""
    for _ in range(steps):
        m = (a + b) / 2
        if f(a) * f(m) <= 0:
            b = m
        else:
            a = m
        yield a, b


def babylonian(y, b0, steps):
    """b -> (b + y/b)/2, the iteration for sqrt(y).  Yields each b."""
    b = b0
    for _ in range(steps):
        b = (b + y / b) / 2
        yield b
