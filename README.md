# BTC Agent Governance

An offline research reference for routing tasks, evaluating evidence, and checking promotion gates.

[中文说明](README.zh.md) · [Portfolio](https://github.com/Daniel-24-life/AIfile)

![Local record viewer for synthetic BTC research governance scenarios](docs/assets/viewer-desktop.png)

## What it demonstrates

- Classify task intent and route it to a permitted research workflow.
- Evaluate evidence declarations before allowing a state change.
- Review four synthetic cases in a static record viewer.

**Stack** · Python, HTML, CSS, JavaScript

## Repository layout

| Path | Contents |
| --- | --- |
| [`orchestrator/`](orchestrator/) | Task routing |
| [`governance/`](governance/) | Evidence and promotion rules |
| [`execution/`](execution/) | Dry-run steps |
| [`demo/`](demo/) | Static record viewer |
| [`tests/`](tests/) | Governance and viewer checks |

## Run locally

```sh
python -B public_demo.py
python -m http.server 4180 --bind 127.0.0.1 --directory demo
```

The first command runs the synthetic scenarios. Open `http://127.0.0.1:4180` to use the viewer.

## Scope and limits

All examples are synthetic. The repository holds no exchange credentials or execution permissions, places no trades, and provides no investment-performance result.

[Architecture](docs/architecture.md) · [Verification](docs/VERIFICATION.md)
