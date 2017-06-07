# We want all percents less than 1 to be prefixed with a 0.
grep -ER "\\$\\.[0-9]*\\\\percent" *
grep -ER "0\.[0-9]*\\\\percent" *

grep -ER "\\$\\.[0-9]*\\$" *


grep -Przo "(?s)Fisher *. *Vector" *.tex
grep -Przo "(?s)Hamming *. *Em" *.tex
grep -Przo "(?s)Selective *. *Match" *.tex
grep -Przo "(?s)Vector *. *of *. *Locally" *.tex
grep -Przo "(?s)invariant *. *feature" *.tex
grep -Przo "(?s)Invariant *. *Feature" *.tex

grep -Er "L2" *.tex
grep -Er "L1" *.tex

grep -ER "[^\\~]\\\\cite" *.tex
grep -Przo "(?s)Deep *. *Face" *.tex

grep -ER "tradeoff" *.tex
grep -ER "precomputed" *.tex

grep -ER "ground-truth" *.tex

Gradient Location-Orientation Histogram
Gradient Location-Orientation Histogram
Speeded Up Robust Features
