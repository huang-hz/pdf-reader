# paseoweb4scholar

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A toolkit for reading, explaining, and writing scholarly literature on [Paseo Web](https://app.paseo.sh).** Three components bound by one loop: read with fidelity, write within the renderer's rules, and let every formula render — and copy back as source LaTeX.

## The loop

```
        read                        write                      render
 ┌─────────────────┐      ┌──────────────────────┐      ┌───────────────────────┐
 │   pdf-reader    │      │   scholarly-output   │      │ paseo-web-latex-      │
 │   (skill)       │ ───▶ │   (skill)            │ ───▶ │ renderer (userscript) │
 │                 │      │                      │      │                       │
 │ PDF ▶ Markdown, │      │ answers follow the   │      │ KaTeX-renders every   │
 │ LaTeX math,     │      │ KaTeX-safe subset    │      │ formula on            │
 │ tables, crops   │      │ and citation norms   │      │ app.paseo.sh          │
 └─────────────────┘      └──────────────────────┘      └───────────────────────┘
```

- **Read** — `pdf-reader` converts a paper into structured Markdown with LaTeX math, tables, and image crops, so the agent works from faithful material.
- **Write** — `scholarly-output` constrains what the agent produces: formulas in the KaTeX-safe subset, disciplined tables and pseudocode, traceable citations.
- **Render** — the Tampermonkey userscript renders LaTeX on Paseo Web and serves source LaTeX on copy. The write-side rules are derived from this renderer's exact behavior; see [COMPATIBILITY.md](COMPATIBILITY.md).

## Components

| Path | Kind | Purpose |
| --- | --- | --- |
| [`skills/pdf-reader`](skills/pdf-reader) | Agent skill | Deep-read PDFs via the MinerU cloud API; answer from high-fidelity Markdown, LaTeX, tables, and crops |
| [`skills/scholarly-output`](skills/scholarly-output) | Agent skill | Output-format discipline for scholarly parsing, explaining, and writing |
| [`userscripts/paseo-web-latex-renderer`](userscripts/paseo-web-latex-renderer) | Tampermonkey userscript | KaTeX rendering + source-LaTeX copy on `app.paseo.sh` |

## Install

Skills (Claude Code and Codex) — on Windows:

```powershell
.\install.ps1
```

This symlinks each directory under `skills/` into `~/.claude/skills/` and `~/.codex/skills/`. Existing symlinks are refreshed; real directories are left untouched with a warning.

Manual equivalent on any platform: link or copy each `skills/<name>` directory into your agent's skills directory.

Userscript: import [`userscripts/paseo-web-latex-renderer/paseo-web-latex-renderer.user.js`](userscripts/paseo-web-latex-renderer/paseo-web-latex-renderer.user.js) into Tampermonkey.

`pdf-reader` additionally needs a MinerU API token — see [its README](skills/pdf-reader/README.md#setup).

## Versioning

The write-side rules in `scholarly-output` are a snapshot of the userscript's detection and rendering behavior. Any change to the userscript's delimiter logic, normalization, or KaTeX version/options must land in the same commit as a rules update — [COMPATIBILITY.md](COMPATIBILITY.md) tracks the correspondence.

## License

[MIT](LICENSE)
