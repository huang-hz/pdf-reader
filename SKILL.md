---
name: pdf-reader
description: Read PDFs in depth with MinerU and answer questions using high-fidelity Markdown, LaTeX, structured tables, and image crops. Use whenever a PDF is attached or referenced, or the user asks to read, summarize, explain, translate, or extract a paper, report, book, formula, table, or figure. Triggers include "read this PDF", "summarize this paper", "extract PDF formulas", "读这篇论文", and "总结这个PDF".
---

# PDF Reader

Use the MinerU Cloud API to convert a PDF, then answer the user's actual question using the resulting structured material. MinerU preserves reading order and produces LaTeX formulas, structured tables, and crops for figures, equations, and tables.

The reusable artifact produced by this skill is the output directory. After conversion, report its path before reading so later turns and other agents can reuse the material without reconverting it.

## Requirements

- A Python 3 interpreter.
- Network access to `https://mineru.net`.
- A MinerU API token from the API management page at `https://mineru.net`.

This workflow intentionally uploads the complete PDF to MinerU. Treat that as normal operation. If the user or environment explicitly forbids third-party processing, do not run the conversion.

## Workflow

1. Resolve `<skill-directory>` as the directory containing this `SKILL.md`. Never hard-code an installation path.

2. Convert the PDF. Quote paths that contain spaces:

```text
python3 "<skill-directory>/scripts/pdf_to_md.py" "<path-to.pdf>"
```

Use another available Python 3 launcher, such as `python` or `py -3`, if `python3` is unavailable.

If `<pdf-directory>/<pdf-stem>_mineru/full.md` already exists, reuse it only when it is newer than the source PDF and its provenance can be verified as belonging to that PDF. If the PDF changed or its provenance is uncertain, convert into a fresh `--out` directory.

- Progress goes to stderr.
- The last stdout line is the extracted Markdown path.
- Output defaults to `<pdf-directory>/<pdf-stem>_mineru/`.
- Pass `--out <directory>` to override the output location.
- Typical conversion takes 30 seconds to 3 minutes. The default timeout is 900 seconds.

3. Report the artifact location before reading. Keep the report to one or two sentences; for example: "PDF conversion completed. The reusable material is at `<output-directory>` (`full.md`, `images/`, and block metadata)."

4. Read `full.md` with the available file-reading tool. For long documents, read it section by section while preserving document structure.

5. Answer from the extracted material:

- Base claims on the document, not prior knowledge. Cite sections or page indices when useful.
- For broad requests, organize the answer as problem, key ideas, method, and results, using the document's own numbers.
- For questions specifically about a figure, inspect the figure crop when image viewing is available.
- Before quoting a formula or pseudocode verbatim, verify any transcription that appears suspicious against the corresponding crop when image viewing is available. If visual verification is unavailable, say so rather than guessing.

## Output Layout

- `full.md`: structured text with LaTeX math, tables, and relative image references.
- `images/`: crops of figures, equations, tables, charts, and algorithms.
- `*_content_list.json`: block metadata with the type, bounding box, page index, and image path.

MinerU may include additional files. Treat `full.md`, `images/`, and the content-list JSON as the standard files for reading the converted document.

## Find Figures and Verification Crops

Figure image filenames are hashes. Search `full.md` for a figure caption using any available text-search tool (`rg`, `grep`, or the client's search tool). The image reference associated with that caption identifies the file under `images/`.

Answer questions about equations and tables from `full.md` first. Use `*_content_list.json` to locate verification crops by `type`, `page_idx`, and `img_path`. Equation crops are usually wide and short.

MinerU can occasionally omit characters such as `<<` or `>>`, or confuse visually similar characters such as `BF16` and `BFl6` in dense formulas or tables. When exact text matters, consult the corresponding crop rather than guessing.

## API Token

The script resolves the token in this order:

1. `--token` command-line argument
2. `MINERU_API_KEY` environment variable
3. `~/.mineru/token`, first line

Prefer the environment variable or token file so the token does not appear in process listings or shell history. If no token is configured, tell the user to configure one outside this conversation; do not ask them to paste it into chat.

## Options

- `--language ch|en`: document language hint. The default, `ch`, also handles English papers.
- `--no-ocr`: disable OCR for a PDF with a reliable text layer.
- `--no-formula`: disable formula parsing.
- `--no-table`: disable table parsing.
- `--timeout <seconds>`: change the conversion timeout.
- `--poll <seconds>`: change the polling interval.

## Troubleshooting

- Retry once after 2 seconds for transient network errors and HTTP `408`, `429`, `500`, `502`, `503`, or `504`.
- For HTTP `401` or a token-related API error, recheck the token sources above.
- For `state: failed`, surface MinerU's `err_msg`; the PDF may be corrupt, unsupported, or over the service limit.
- On timeout, retry with `--timeout 1800` for a large document.
