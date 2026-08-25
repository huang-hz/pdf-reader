# Compatibility

`skills/scholarly-output`'s rendering rules are a snapshot of
`userscripts/paseo-web-latex-renderer`'s behavior. When the userscript changes
its delimiter detection, normalization fixes, raw-source-block heuristic, or
KaTeX version/options, update the skill's rules in the same commit and add a
row here.

| scholarly-output rules | Userscript | KaTeX | Snapshot covers |
| --- | --- | --- | --- |
| v5 (current) | v2.3.5 | 0.16.21 | v4 plus a hard brace-transport rule: ordinary visible set braces are always `\lbrace ... \rbrace`; direct and `\left`/`\right` forms using `\{` / `\}` are prohibited because Markdown can strip their brace escapes before KaTeX receives the source. |
| v4 | v2.3.5 | 0.16.21 | v3 plus a hard three-line block-math transport invariant: one complete equation source line between `$$` delimiters, so Markdown cannot consume standalone equalities before KaTeX receives them. |
| v3 | v2.3.5 | 0.16.21 | Same formula syntax and KaTeX behavior as v2.3.4; ordinary DOM scanning is restricted to assistant messages, so user-authored LaTeX stays source text. |
| v3 | v2.3.4 | 0.16.21 | v2 rules plus `\cr` rather than `\\` for rows in `aligned`/`cases`-style environments. This avoids Markdown reducing a row separator before rendering while React raw-source recovery remains disabled by default for long-conversation performance. |
| v2 | v2.3.4 | 0.16.21 | Same renderer as v1; scholarly output now prevents Markdown transport loss at the source by preferring `\lbrace` / `\rbrace` and prohibiting lone operator lines; `throwOnError: false`, `strict: "ignore"`, `trust: false` |
| v1 | v2.3.4 | 0.16.21 | Delimiter set (`$$`/`\[...\]` display, `$...$`/`\(...\)` inline); standalone-`$$` display rule; inline math heuristic; `\tag` forces display; `normalizeLatex` fixes (`1.56%`, `\ &\`); `{\color...}` raw-source-block skip; `throwOnError: false`, `strict: "ignore"`, `trust: false` |
