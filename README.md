# x_make_markdown_x — Control Room Lab Notes

> "If the documentation isn't as tight as the cook, the operation falls apart. This rig keeps the words as sharp as the product."

## Manifesto
x_make_markdown_x automates Markdown generation—component registries, PDF exports, accessibility linting, and more. It's how I broadcast the Road to 0.20.2 truth with consistent structure and zero wasted motion.

## 0.20.2 Command Sequence
Version 0.20.2 gives every document the same ruthless clarity I use on the line. This README mirrors the Road to 0.20.2 brief—no drift, no ambiguity, just controlled output ready for distribution.

## Ingredients
- Python 3.11+
- Ruff, Black, MyPy, and Pyright
- Optional: Pandoc or wkhtmltopdf for PDF production, depending on the adapter you enable

## Cook Instructions
1. `python -m venv .venv`
2. `.\.venv\Scripts\Activate.ps1`
3. `python -m pip install --upgrade pip`
4. `pip install -r requirements.txt`
5. `python x_cls_make_markdown_x.py --help` to enumerate generation recipes before you publish

## Quality Assurance
| Check | Command |
| --- | --- |
| Formatting sweep | `python -m black .`
| Lint interrogation | `python -m ruff check .`
| Type audit | `python -m mypy .`
| Static contract scan | `python -m pyright`
| Functional verification | `pytest`

## Distribution Chain
- [Changelog](./CHANGELOG.md)
- [Road to 0.20.2 Control Room Ledger](../x_0_make_all_x/Change%20Control/0.20.2/Road%20to%200.20.2%20Engineering%20Proposal.md)
- [Road to 0.20.2 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.2/Road%20to%200.20.2%20Engineering%20Proposal.md)

## Cross-Linked Intelligence
- [x_make_graphviz_x](../x_make_graphviz_x/README.md) — feeds diagrams straight into Markdown drops
- [x_make_mermaid_x](../x_make_mermaid_x/README.md) — complements this generator with Mermaid storyboards
- [x_0_make_all_x](../x_0_make_all_x/README.md) — orchestrator uses this repo to package release notes and proposals

## Lab Etiquette
Accessibility, linting, export formats—document every new component in the Change Control index and verify the outputs match the lab's tone. No filler, no fluff.
