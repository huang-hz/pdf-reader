---
name: scholarly-output
description: Output-format discipline for scholarly work — formulas, tables, pseudocode, citations — so answers about scientific literature render correctly and stay faithful in chat interfaces where LaTeX is KaTeX-rendered (such as Paseo Web). Use when parsing, explaining, or writing about papers, whenever a reply will contain LaTeX math, tables, or pseudocode, or when a formula appears as red raw text. Triggers include "讲解这篇论文", "公式渲染失败", "write up this result", and "red unrendered formula".
---

# Scholarly Output

Rules for producing scholarly answers that render correctly and stay faithful to the source.

The rendering surface is KaTeX 0.16 delivered by the paseo-web-latex-renderer userscript (v2.3.4), with `throwOnError: false`: invalid LaTeX does not degrade gracefully — it appears as red raw source in the chat. What you write is also what the user copies, so the source text is the product.

## Formula Rules (render layer)

Derived from the renderer; see `COMPATIBILITY.md` at the repository root for the version correspondence.

### Delimiters

- Display math: `$$...$$` **on its own line** — nothing else before or after the delimiters on those lines — or `\[...\]`. A `$$` that shares a line with other text renders inline.
- Inline math: `$...$` or `\(...\)`. Inline content must contain a math signal character (`\ ^ _ { } = + - * / < > |`) or be one to three letters. Pure numbers like `$0.5$` intentionally do not render — that is the renderer protecting currency text, not a bug.
- `\tag{...}` is valid only in display math. Always place tagged equations in a `$$` block.

### KaTeX-safe LaTeX

- `\left` and `\right` must pair, and the token immediately after each must be a valid delimiter. For visible braces, prefer `\left\lbrace ... \right\rbrace` (or `\left. ... \right\rbrace` on one side). `\left{` is a syntax error — a bare `{` is a grouping character, not a delimiter. Although `\left\{ ... \right\}` is valid TeX, Paseo Markdown can consume the brace escape before DOM rendering; source output must use `\lbrace` / `\rbrace` instead.
- Escape percent as `\%` inside math. The renderer auto-fixes `1.56%`, but do not rely on it.
- A bare `&` is invalid outside an alignment environment (`aligned`, `gathered`, `cases`, `split`, `array`, `matrix` and its variants). Use an environment, or `\mathbin{\&}` for a literal ampersand operator.
- Multi-character sub/superscripts need braces: `x_{ij}`, not `x_ij`.
- Use only KaTeX-supported commands. Not supported here: `\href` / `\url` (`trust: false`), `\cite`, `\ref`, `\eqref`, `\footnote`, `\bibliography`, `\includegraphics`, `\emph`, and float or text environments such as `\begin{figure}` or `\begin{algorithm}`. Prose styling belongs to Markdown (`*emphasis*`), not LaTeX text commands.
- Never start a formula or a message block with a bare `{\color ...}` group — the renderer treats such blocks as raw source and skips them. Use `\color{...}` inside math normally.

### Coexistence with Markdown

The chat pipeline parses Markdown before the renderer ever sees the text:

- **No lone-operator lines inside math.** Never let a line inside a `$$` block consist only of `=` or `-` characters. Markdown reads such a line as a Setext heading underline: it consumes the line above and splits the formula. Attach the operator to an adjacent line instead:
  - Bad: `\mathcal Z(T_r,\mathbf s^*)` / `=` / `\left\lbrace` on three lines
  - Good: `\mathcal Z(T_r,\mathbf s^*) =` / `\left\lbrace`
- For a short or medium display formula, keep all math on one physical line between the `$$` delimiters. Do not reflow it for prose readability after linting. Use a KaTeX `aligned` block only when a multiline formula is genuinely necessary.
- Outside math, never place a line consisting only of `=` or `-` directly under text either — the same Setext rule consumes the line above.
- Prefer `\cdot` or `\times` over a bare `*` adjacent to letters, which Markdown can parse as emphasis.
- Fenced code blocks are never scanned for math — the safe place for literal LaTeX source.

## Tables, Pseudocode, Citations (convention layer)

- Tables: Markdown tables only. Keep columns narrow, put units in the header row, and avoid line breaks or nested blocks inside cells.
- Pseudocode and algorithms: fenced code blocks (` ```text `). Never LaTeX algorithm environments.
- Citing the source document: anchor claims as `(Section 4.2)`, `(Figure 6)`, `(Table 3)`, adding a page index when useful. These anchors match the pdf-reader skill's output layout so the user can trace every claim back to the material.
- Quoting a formula from a parsed PDF: quote the source exactly. If a transcription looks suspicious (dropped `<<` / `>>`, confusions like `BF16` vs `BFl6`), verify against the corresponding crop first — see the pdf-reader skill.
- Terminology: on first use give the bilingual pair (e.g. 量化缩放因子 / quantization scale), then stay consistent.

## Self-check Before Sending

When a reply contains non-trivial math, lint the **exact final Markdown** first:

```text
python3 "<skill-directory>/scripts/lint_latex.py" draft.md
cat draft.md | python3 "<skill-directory>/scripts/lint_latex.py"
```

Resolve `<skill-directory>` as the directory containing this `SKILL.md`; never hard-code an installation path. Use another Python 3 launcher (`python`, `py -3`) if `python3` is unavailable. Do not lint a separately assembled formula list: the lint input must contain the same math blocks and line breaks that will be sent. If writing a draft file is unavailable, pipe the exact final Markdown to the linter; after it passes, do not reflow or edit its formulas.

The linter extracts math spans (skipping code blocks, as the renderer does) and flags the failure modes above: bare `\left{`-class delimiter errors, Markdown-fragile `\left\{` / `\right\}` spellings, unescaped `%`, bare `&`, inline `\tag`, unsupported commands and environments, unbalanced braces, Setext hazards. A Setext line **inside** a formula is an error (it corrupts what the renderer receives); outside a formula it is a warning. When Node.js with the `katex` package is installed, it additionally renders every formula with `throwOnError` enabled for ground truth; otherwise it reports rule-based results only. Fix every error before sending.
