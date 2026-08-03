# pdf-reader

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**High-fidelity PDF reading for AI agents.** Turns any PDF into structured reading material — LaTeX formulas, structured tables, and image crops of every figure, equation, and table — so the agent can answer questions with the fidelity the document deserves.

A skill for Claude Code, Codex, OpenCode, and compatible agents.

---

## Why

Academic PDFs are hostile to plain-text extraction: fractions flatten, superscripts vanish, columns interleave, and figures disappear entirely. pdf-reader converts a PDF into material an agent can actually reason about:

| Region | Becomes |
| --- | --- |
| Text | Clean Markdown, reading order preserved |
| Formulas | LaTeX (`$...$` / `$$...$$`), structure intact |
| Tables | Structured tables, plus a region crop |
| Figures | Image crops, referenced inline in the Markdown |
| Equations & tables | Also saved as verification crops — ground truth when a transcription looks suspicious |

## How it works

```
paper.pdf  ──▶  MinerU cloud API  ──▶  paper_mineru/
                                       ├── full.md               structured text, LaTeX math, tables, figure refs
                                       ├── images/               figure + equation + table crops
                                       └── *_content_list.json   per-block metadata (type, bbox, page, image path)
```

The agent then reads `full.md`, resolves "Figure N" to its image via the caption anchor, and verifies any suspect formula or pseudocode against its crop before quoting it.

## Install

Clone into your agent's skills directory — e.g. for Claude Code:

```bash
git clone https://github.com/<your-account>/pdf-reader.git ~/.claude/skills/pdf-reader
```

## Setup

Get an API token at [mineru.net](https://mineru.net) (API management page), then either:

```bash
export MINERU_API_KEY=<token>
```

or

```bash
mkdir -p ~/.mineru && printf '%s\n' '<token>' > ~/.mineru/token
```

> Conversion uploads the complete PDF to MinerU. Don't use this with documents that can't leave your machine.

## Usage

Just ask your agent about a PDF:

- "Summarize this paper: `./paper.pdf`"
- "Extract Table 3 and the equations in section 4"
- "这篇论文的 Figure 6 画了什么？"

Or run the converter directly:

```bash
python3 scripts/pdf_to_md.py paper.pdf
# → <paper_dir>/paper_mineru/full.md
```

| Flag | Effect |
| --- | --- |
| `--language ch\|en` | Language hint (default `ch`, also handles English) |
| `--no-ocr` | Skip OCR for text-layer PDFs |
| `--no-formula`, `--no-table` | Skip formula / table parsing |
| `--out <dir>` | Custom output directory |
| `--timeout <s>` | Conversion timeout (default 900 s) |

## License

[MIT](LICENSE)
