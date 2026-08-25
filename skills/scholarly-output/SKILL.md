---
name: scholarly-output
description: Output-format discipline for scholarly work — formulas, tables, pseudocode, citations — so answers about scientific literature render correctly and stay faithful in chat interfaces where LaTeX is KaTeX-rendered (such as Paseo Web). Use when parsing, explaining, or writing about papers, whenever a reply will contain LaTeX math, tables, or pseudocode, or when a formula appears as red raw text. Triggers include "讲解这篇论文", "公式渲染失败", "write up this result", and "red unrendered formula".
---

# Scholarly Output

Rules for producing scholarly answers that render correctly and stay faithful to the source.

The rendering surface is KaTeX 0.16 delivered by the paseo-web-latex-renderer userscript (v2.3.5), with `throwOnError: false`: invalid LaTeX does not degrade gracefully — it appears as red raw source in the chat. What you write is also what the user copies, so the source text is the product.

## Formula Rules (render layer)

Derived from the renderer; see `COMPATIBILITY.md` at the repository root for the version correspondence.

### Delimiters

- Display math: `$$...$$` **on its own line** — nothing else before or after the delimiters on those lines — or `\[...\]`. A `$$` that shares a line with other text renders inline.
- Inline math: `$...$` or `\(...\)`. Inline content must contain a math signal character (`\ ^ _ { } = + - * / < > |`) or be one to three letters. Pure numbers like `$0.5$` intentionally do not render — that is the renderer protecting currency text, not a bug.
- `\tag{...}` is valid only in display math. Always place tagged equations in a `$$` block.

### KaTeX-safe LaTeX

- **Brace transport rule (highest priority).** For an ordinary set or any other visible pair of braces, write `\lbrace ... \rbrace` directly. Do **not** put `\left` or `\right` around those braces, even though TeX would normally allow it. Never emit `\{` or `\}` for visible braces either. In this chat pipeline, all six spellings `\{`, `\}`, `\left{`, `\right}`, `\left\{`, and `\right\}` are forbidden: the bare `\left` / `\right` forms are invalid TeX, and Markdown can strip the brace escape from the other forms before KaTeX sees them. Use these source forms exactly:
  ```text
  $$
  (\mathcal{P}c)(y)\in\lbrace \frac{c}{2},c,\frac{3c}{2}\rbrace.
  $$
  ```
  ```text
  $$
  \lbrace 0,\theta,2\theta,\ldots,(2^T-1)\theta\rbrace.
  $$
  ```
- `\left` and `\right` must pair, and the token immediately after each must be a valid delimiter. Use them only where dynamic sizing is genuinely needed with a non-brace delimiter, or use `\left. ... \right\rbrace` for a one-sided construct.
- Escape percent as `\%` inside math. The renderer auto-fixes `1.56%`, but do not rely on it.
- A bare `&` is invalid outside an alignment environment (`aligned`, `gathered`, `cases`, `split`, `array`, `matrix` and its variants). Use an environment, or `\mathbin{\&}` for a literal ampersand operator.
- Multi-character sub/superscripts need braces: `x_{ij}`, not `x_ij`.
- Use only KaTeX-supported commands. Not supported here: `\href` / `\url` (`trust: false`), `\cite`, `\ref`, `\eqref`, `\footnote`, `\bibliography`, `\includegraphics`, `\emph`, and float or text environments such as `\begin{figure}` or `\begin{algorithm}`. Prose styling belongs to Markdown (`*emphasis*`), not LaTeX text commands.
- Never start a formula or a message block with a bare `{\color ...}` group — the renderer treats such blocks as raw source and skips them. Use `\color{...}` inside math normally.

### Coexistence with Markdown

The chat pipeline parses Markdown before the renderer ever sees the text:

- **Hard block-math transport invariant (highest priority).** For every short or medium display equation, use exactly three physical source lines: opening `$$`, one complete equation line, closing `$$`. Do not visually reflow the equation. In particular, never put `=`, `-`, `+`, `\le`, `\ge`, or any relation/operator token on a line by itself, or directly before/after a line break. Markdown can consume a lone `=` as a Setext heading underline before KaTeX receives the formula.
  - Required form:
    ```text
    $$
    I(z)=0\cdot4+0\cdot2+4\cdot1=4.
    $$
    ```
  - Forbidden form — it loses the equalities in Paseo Markdown:
    ```text
    $$
    I(z)
    =
    0\cdot4+0\cdot2+4\cdot1
    =
    4.
    $$
    ```
- If a derivation genuinely needs multiple visual rows, keep the entire environment on that one interior source line and use `\cr` for its rows, for example: `$$\begin{aligned}I(z)&=0\cdot4+0\cdot2+4\cdot1\cr &=4.\end{aligned}$$`. Never use actual source line breaks to align equality signs.
- **Use `\cr`, never `\\`, to separate rows inside `aligned`, `cases`, `gathered`, `split`, or `array` environments.** The performance-oriented renderer normally reads Markdown's DOM text, where Markdown reduces `\\` to `\`; the next row then becomes an invalid control sequence such as `\s`, `\u`, or `\1`. KaTeX 0.16 supports `\cr`, and Markdown preserves it. Keep the environment in one display block, for example: `$$\begin{cases}0,&t<T_r,\cr 1,&t\ge T_r.\end{cases}$$`.
- Do not compensate with four backslashes. It makes copied LaTeX ambiguous and is unnecessary with `\cr`.
- Outside math, never place a line consisting only of `=` or `-` directly under text either — the same Setext rule consumes the line above.
- Prefer `\cdot` or `\times` over a bare `*` adjacent to letters, which Markdown can parse as emphasis.
- Fenced code blocks are never scanned for math — the safe place for literal LaTeX source.
- Apply these constraints directly while composing the final answer; do not add a separate formatting-validation tool call.

## Tables, Pseudocode, Citations (convention layer)

- Tables: Markdown tables only. Keep columns narrow, put units in the header row, and avoid line breaks or nested blocks inside cells.
- Pseudocode and algorithms: fenced code blocks (` ```text `). Never LaTeX algorithm environments.
- Citing the source document: anchor claims as `(Section 4.2)`, `(Figure 6)`, `(Table 3)`, adding a page index when useful. These anchors match the pdf-reader skill's output layout so the user can trace every claim back to the material.
- Quoting a formula from a parsed PDF: quote the source exactly. If a transcription looks suspicious (dropped `<<` / `>>`, confusions like `BF16` vs `BFl6`), verify against the corresponding crop first — see the pdf-reader skill.
- Terminology: on first use give the bilingual pair (e.g. 量化缩放因子 / quantization scale), then stay consistent.
