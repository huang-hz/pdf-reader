# lint smoke cases

## Case 1: the 2026-08-21 failure (must error twice)

$$
\left{
R_{\mathrm{TWE}}(0),
R_{\mathrm{TWE}}(1)
\right}{0,1}.
$$

## Case 2: healthy display formula (must pass)

$$
m_{MBS}^8 = \left(\mathrm{bits}\left(\frac{6.0}{\alpha_{max}^{128}}\right) \mathbin{\&} 0x007F8000\right) \gg 15
$$

Inline $x_i$ works.
Pure number $42$ never renders.
An unclosed $0.5 stays literal.

## Case 3: assorted violations

Inline tag: \(\hat{x} = x + q, \tag{3}\)

Bare ampersand: $A \& B$ is fine, $A & B$ is not.

Percent: the ratio is $96.5%$ here.

Multi-char script: $alpha_max$ without braces.

Setext hazard below this line:
====

```text
\left{ inside a fenced code block must be ignored }
```
