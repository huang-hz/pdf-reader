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

## Case 4: Markdown-brace transport (first block must error; second must pass)

`\left\{` is valid TeX but Paseo Markdown can consume its brace escape before
the renderer reads DOM text. Prefer the delimiter macros in the safe rewrite.

$$
\mathcal V_z=[-Z,Z]^T,
\qquad
\mathcal Z(T_r,\mathbf s^*) =
\left\{
\mathbf z\in\mathcal V_z
\mid
s[t+T_r]=s^*[t],\ \forall t
\right\}.
$$

Safe rewrite (must pass):

$$
\mathcal V_z=[-Z,Z]^T,
\qquad
\mathcal Z(T_r,\mathbf s^*) =
\left\lbrace
\mathbf z\in\mathcal V_z
\mid
s[t+T_r]=s^*[t],\ \forall t
\right\rbrace.
$$

## Case 5: lone `=` inside display math (must error)

$$
\mathcal C_T
=
\left\lbrace
\theta k\ \middle|\ k=0,1,\ldots,2^T-1
\right\rbrace.
$$
