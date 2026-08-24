# Compatibility

`skills/scholarly-output`'s rendering rules are a snapshot of
`userscripts/paseo-web-latex-renderer`'s behavior. When the userscript changes
its delimiter detection, normalization fixes, raw-source-block heuristic, or
KaTeX version/options, update the skill's rules in the same commit and add a
row here.

| scholarly-output rules | Userscript | KaTeX | Snapshot covers |
| --- | --- | --- | --- |
| v2 (current) | v2.3.4 | 0.16.21 | Same renderer as v1; scholarly output now prevents Markdown transport loss at the source by preferring `\lbrace` / `\rbrace`, prohibiting lone operator lines, and linting the exact final Markdown before it is sent; `throwOnError: false`, `strict: "ignore"`, `trust: false` |
| v1 | v2.3.4 | 0.16.21 | Delimiter set (`$$`/`\[...\]` display, `$...$`/`\(...\)` inline); standalone-`$$` display rule; inline math heuristic; `\tag` forces display; `normalizeLatex` fixes (`1.56%`, `\ &\`); `{\color...}` raw-source-block skip; `throwOnError: false`, `strict: "ignore"`, `trust: false` |
