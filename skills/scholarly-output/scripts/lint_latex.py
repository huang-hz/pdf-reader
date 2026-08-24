#!/usr/bin/env python3
"""Lint draft Markdown for formulas that will fail or misrender under the
paseo-web-latex-renderer (userscript v2.3.4, KaTeX 0.16.21).

Usage:
    python3 lint_latex.py draft.md
    cat draft.md | python3 lint_latex.py

Rule-based checks always run. If Node.js with the `katex` package is
available, every formula is also rendered with throwOnError enabled.
Exit code is 1 when any error-level finding exists.
"""

import json
import re
import shutil
import subprocess
import sys

SPAN_RE = re.compile(
    r"""
    (?<!\\)\$\$(?P<dd>.+?)(?<!\\)\$\$
  | (?<!\\)\\\[(?P<db>.+?)(?<!\\)\\\]
  | (?<!\\)\\\((?P<ib>.+?)(?<!\\)\\\)
  | (?<![\\$])\$(?!\$)(?P<im>[^$\n]+?)(?<![\\$])\$(?!\$)
""",
    re.DOTALL | re.VERBOSE,
)

ALIGN_ENVS = (
    "aligned", "gathered", "split", "cases", "dcases", "rcases", "array",
    "matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix",
    "subarray", "alignedat", "align", "align*", "equation", "equation*",
    "gather", "gather*", "eqnarray", "eqnarray*",
)
ALIGN_ENV_RE = re.compile(r"\\begin\{(?:" + "|".join(ALIGN_ENVS) + r")\}")
UNSUPPORTED_CMD_RE = re.compile(
    r"\\(cite|ref|eqref|footnote|bibliography|href|url|emph|includegraphics)\b"
)
UNSUPPORTED_ENV_RE = re.compile(
    r"\\begin\{(figure\*?|table\*?|algorithm|algorithmic|enumerate|itemize|"
    r"description|document|center|minipage)\}"
)
BAD_LR_DELIM_RE = re.compile(r"\\(?:left|right)\s*[{}]")
MARKDOWN_BRACE_ESCAPE_RE = re.compile(r"\\(?:left|right|middle)\s*\\[{}]")
UNESCAPED_PERCENT_RE = re.compile(r"(?<!\\)%")
BARE_AMP_RE = re.compile(r"(?<!\\)&")
TAG_RE = re.compile(r"\\tag\*?\s*\{")
MULTICHAR_SCRIPT_RE = re.compile(r"(?<!\\)[_^][A-Za-z0-9]{2,}")
COLOR_GROUP_RE = re.compile(r"^\{\s*\\(?:color|textcolor)\s*\{")
PURE_NUMBER_RE = re.compile(r"^\d+(?:[.,]\d+)?$")

findings = []


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def add(line, level, message, snippet=""):
    findings.append((line, level, message, snippet.strip().replace("\n", " ")[:80]))


def strip_code(text):
    """Blank out fenced code blocks and inline code; the renderer skips them."""
    text = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), text)
    return text


def is_standalone_dd(text, start, end):
    line_start = text.rfind("\n", 0, start) + 1
    nl = text.find("\n", end)
    line_end = len(text) if nl == -1 else nl
    return not text[line_start:start].strip() and not text[end:line_end].strip()


def check_span(text, start, end, latex, display, inline_kind):
    line = line_of(text, start)
    snippet = latex

    m = BAD_LR_DELIM_RE.search(latex)
    if m:
        add(line, "error",
            "bare brace after \\left/\\right; write \\left\\lbrace ... \\right\\rbrace",
            snippet)
    if MARKDOWN_BRACE_ESCAPE_RE.search(latex):
        add(line, "error",
            "Paseo Markdown can consume \\{ / \\} before DOM rendering; "
            "write \\left\\lbrace ... \\right\\rbrace instead",
            snippet)
    if latex.count("\\left") != latex.count("\\right"):
        add(line, "error", "unpaired \\left / \\right", snippet)
    if UNESCAPED_PERCENT_RE.search(latex):
        add(line, "error", "unescaped % in math; write \\%", snippet)
    if BARE_AMP_RE.search(latex) and not ALIGN_ENV_RE.search(latex):
        add(line, "error",
            "bare & outside an alignment environment; use aligned/cases "
            "or \\mathbin{\\&}", snippet)
    if TAG_RE.search(latex) and not display:
        add(line, "warning",
            "\\tag in inline delimiters; the renderer upgrades it to display, "
            "but a $$ block is the reliable form", snippet)
    m = UNSUPPORTED_CMD_RE.search(latex)
    if m:
        add(line, "error",
            f"\\{m.group(1)} is not supported by this KaTeX setup", snippet)
    m = UNSUPPORTED_ENV_RE.search(latex)
    if m:
        add(line, "error",
            f"\\begin{{{m.group(1)}}} is not a KaTeX math environment",
            snippet)

    body = latex.replace("\\{", "").replace("\\}", "")
    if body.count("{") != body.count("}"):
        add(line, "error", "unbalanced braces", snippet)

    begins = re.findall(r"\\begin\{([^}]+)\}", latex)
    ends = re.findall(r"\\end\{([^}]+)\}", latex)
    if sorted(begins) != sorted(ends):
        add(line, "error", "\\begin / \\end mismatch", snippet)

    if MULTICHAR_SCRIPT_RE.search(latex):
        add(line, "warning",
            "multi-character sub/superscript without braces (x_ij); "
            "write x_{ij}", snippet)
    if COLOR_GROUP_RE.search(latex.strip()):
        add(line, "warning",
            "formula starts with a bare {\\color...} group; the renderer "
            "skips such blocks as raw source", snippet)
    if inline_kind == "im" and PURE_NUMBER_RE.search(latex.strip()):
        add(line, "info",
            "pure number in $...$ does not render as math (by design)", snippet)
    if inline_kind == "dd" and not is_standalone_dd(text, start, end):
        add(line, "warning",
            "$$ shares its line with other text; renders inline, "
            "not display", snippet)


def katex_render(spans):
    if not shutil.which("node"):
        return None
    probe = subprocess.run(
        ["node", "-e", "require.resolve('katex')"],
        capture_output=True, text=True,
    )
    if probe.returncode != 0:
        return None

    js = (
        "const k=require('katex');let d='';process.stdin.on('data',c=>d+=c)"
        ".on('end',()=>{const r=JSON.parse(d).map(s=>{try{"
        "k.renderToString(s.latex,{displayMode:s.display,throwOnError:true,"
        "strict:'ignore',trust:false,output:'mathml'});return{i:s.i,ok:true}"
        "}catch(e){return{i:s.i,ok:false,error:String(e.message||e)}}});"
        "process.stdout.write(JSON.stringify(r))});"
    )
    payload = [{"i": i, "latex": s["latex"], "display": s["display"]}
               for i, s in enumerate(spans)]
    out = subprocess.run(["node", "-e", js], input=json.dumps(payload),
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    return json.loads(out.stdout)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        with open(sys.argv[1], encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    text = strip_code(raw)
    spans = []
    for m in SPAN_RE.finditer(text):
        kind = m.lastgroup
        latex = m.group(kind)
        if not latex.strip():
            continue
        if kind == "dd":
            display = is_standalone_dd(text, m.start(), m.end()) or bool(TAG_RE.search(latex))
        elif kind == "db":
            display = True
        else:
            display = False
        spans.append({"latex": latex, "display": display,
                      "start": m.start(), "end": m.end(), "kind": kind})
        check_span(text, m.start(), m.end(), latex, display, kind)

    for match in re.finditer(r"(?m)^([=-]+)\s*$", text):
        prev_end = match.start() - 1
        if prev_end >= 0 and text[:match.start()].rstrip("\n") and \
                text[:match.start()].rstrip("\n")[-1] != "\n":
            in_math = any(s["start"] <= match.start() < s["end"]
                          for s in spans)
            if in_math:
                add(line_of(text, match.start()), "error",
                    "lone '=' / '-' line inside a formula: Markdown consumes "
                    "it as a Setext heading underline, splits the block, and "
                    "unescapes \\{ to { — the renderer then fails on the "
                    "corrupted source; attach the operator to an adjacent line",
                    match.group(0))
            else:
                add(line_of(text, match.start()), "warning",
                    "line of only '=' or '-': Markdown reads it as a Setext "
                    "heading underline and consumes the previous line",
                    match.group(0))

    results = katex_render(spans)
    if results is None:
        print("note: node+katex unavailable; rule-based checks only.",
              file=sys.stderr)
    else:
        for res in results:
            if not res["ok"]:
                s = spans[res["i"]]
                add(line_of(text, s["start"]), "error",
                    f"KaTeX render failed: {res['error']}", s["latex"])

    findings.sort(key=lambda f: (f[0], f[1]))
    for line, level, message, snippet in findings:
        suffix = f"  :: {snippet}" if snippet else ""
        print(f"L{line:<5} {level:<8} {message}{suffix}")

    errors = sum(1 for f in findings if f[1] == "error")
    warnings = sum(1 for f in findings if f[1] == "warning")
    print(f"\n{len(spans)} formula span(s), {errors} error(s), "
          f"{warnings} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
