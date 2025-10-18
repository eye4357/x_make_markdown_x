# x_make_markdown_x — Control Room Lab Notes

> "If the documentation isn't as tight as the cook, the operation falls apart. This rig keeps the words as sharp as the product."

## Manifesto
x_make_markdown_x automates Markdown generation—component registries, PDF exports, accessibility linting, and more. It's how I broadcast the Road to 0.20.4 truth with consistent structure and zero wasted motion.

## 0.20.4 Command Sequence
Version 0.20.4 welds the generator to the shared exporters in `x_make_common_x`. Markdown drops now flow through `export_markdown_to_pdf`, capture `ExportResult` metadata, and register deterministic PDF paths inside the orchestrator summary so the Kanban board shows hard evidence instead of fiction.

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
- [Road to 0.20.4 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.4/Road%20to%200.20.4%20Engineering%20Proposal.md)
- [Road to 0.20.3 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.3/Road%20to%200.20.3%20Engineering%20Proposal.md)

## Reconstitution Drill
The monthly rebuild drills this generator from scratch. Install wkhtmltopdf on the sacrificial machine, rerun the exporters, confirm Markdown and PDF outputs match the orchestrator summary wiring, and log binary versions. Any friction gets written back into this README and the Change Control runbook before the next release window.

## Cross-Linked Intelligence
- [x_make_graphviz_x](../x_make_graphviz_x/README.md) — feeds diagrams straight into Markdown drops
- [x_make_mermaid_x](../x_make_mermaid_x/README.md) — complements this generator with Mermaid storyboards
- [x_0_make_all_x](../x_0_make_all_x/README.md) — orchestrator uses this repo to package release notes and proposals

## Lab Etiquette
Accessibility, linting, export formats—document every new component in the Change Control index and verify the outputs match the lab's tone. No filler, no fluff.

## Sole Architect Profile
- I am the lone author behind every generator, linter, and exporter pathway in this project. Years of technical writing fused with automation engineering give me absolute control over content pipelines.
- Benevolent dictatorship here means the same mind governs narrative strategy, build scripts, and PDF emission, guaranteeing alignment across the documentation stack.

## Legacy Workforce Costing
- Classical delivery would assign: 1 lead documentation engineer, 1 automation developer, 1 build engineer for PDF tooling, and 1 technical editor.
- Effort projection: 10-12 engineer-weeks to rebuild the generator, exporters, and compliance checks without modern AI accelerants.
- Cost expectation: USD 80k–105k for the initial build, plus ongoing maintenance for exporter drift and accessibility audits.

## Techniques and Proficiencies
- Mastery over documentation automation, exporter design, and accessibility linting—delivered as a solo practitioner.
- Adept at weaving narrative control with code quality, ensuring artifacts satisfy investors, auditors, and engineers simultaneously.
- Comfortable translating strategic roadmap messaging into reproducible Markdown/PDF pipelines with zero external dependencies.

## Stack Cartography
- Language and Framework: Python 3.11+, Jinja-style templating strategies, pathlib-based asset management.
- Export Infrastructure: Shared exporters from `x_make_common_x`, wkhtmltopdf pipeline, optional Pandoc adapters.
- Tooling Discipline: Ruff, Black, MyPy, Pyright, pytest, Markdown lint configurations.
- Integration Points: Orchestrator hooks in `x_0_make_all_x`, diagram ingestion from Graphviz and Mermaid siblings, Change Control evidence capture.
