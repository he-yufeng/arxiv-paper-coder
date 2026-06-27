# arxiv-paper-coder

A multi-agent system that turns a natural-language brief into a working codebase. A planner
decomposes the task, a coder writes the files, and a reviewer checks the result — all coordinated
by an orchestrator that tracks dependencies, memory, and artifacts. It ships with an arXiv pipeline
that builds a daily CS-papers website end to end.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## How it works

Three agents and an orchestrator run a Reason–Act–Reflect loop:

- **Planner** — breaks the brief into tasks and builds a dependency graph (networkx DAG).
- **Coder** — implements each task, calling tools for file I/O, code execution, web/arXiv access, and templating.
- **Reviewer** — checks quality, flags problems, and feeds corrections back into the loop.
- **Orchestrator** — schedules tasks, resolves dependencies, and manages shared memory and generated artifacts.

```
                         Orchestrator (core engine)
                Task scheduler · Memory · Dependency resolver
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
       Planning agent  ──▶    Coding agent   ──▶    Review agent
       task decomp,           code gen,             quality checks,
       chain-of-thought,      tool calling,         testing,
       dependency DAG         artifact mgmt         feedback
            └──────────────────────┼──────────────────────┘
                                   ▼
                  Tool layer: file I/O · code execution
                  web search · arXiv API · Jinja2 templates · git
```

The design borrows from a few familiar patterns: ReAct (Yao et al., 2022), chain-of-thought
prompting (Wei et al., 2022), and self-reflection.

## Install

```bash
git clone https://github.com/he-yufeng/arxiv-paper-coder
cd arxiv-paper-coder
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env        # then add an API key
```

## Configuration

Models and keys are read from the environment (see `env.example`). Pick the model with
`DEFAULT_MODEL` — anything your provider supports:

```
DEFAULT_MODEL=anthropic/claude-opus-4.5
OPENAI_API_KEY=...         # or QWEN_API_KEY, a DeepSeek base URL, etc.
```

Each role can override the default with `PLANNER_MODEL`, `CODER_MODEL`, or `REVIEWER_MODEL`.

## Usage

The CLI entry point is `run_agent.py`:

```bash
# interactive mode
python run_agent.py

# one-shot from a prompt
python run_agent.py --prompt "生成 arXiv 论文展示网页"

# send the generated project to a chosen directory
python run_agent.py --prompt "build a todo web app" --output ./my_project
```

Generated projects land under `outputs/generated_projects/` unless `--output` says otherwise.

To drive it from Python:

```python
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator(project_name="my_project")
results = orchestrator.execute_project(
    objective="Fetch data from an API and show it in a dashboard"
)
```

## The arXiv CS Daily demo

`Prompt.txt` holds the brief for the bundled example — a static "arXiv CS Daily" site with paper
ingestion, tagging, and a generated UI. Feed it to the agent to reproduce the site end to end; the
HTML templates and static assets it builds against live under `web/`.

## Layout

```
src/
  core/        orchestrator, config, parallel LLM pool
  agents/      planner, coder, reviewer
  tools/       file I/O, code execution, web/arXiv, templating
  memory/      context and artifact tracking
  tasks/       task models
web/           static assets + Jinja2 templates for generated sites
docs/          architecture, quickstart, API, agent task matrix
tests/         agent, tool, and API-pool tests
run_agent.py   CLI entry point
```

## Docs

- [Quickstart](docs/quickstart.md)
- [Architecture](docs/architecture.md)
- [API reference](docs/api.md)

## Related Projects

arxiv-paper-coder is one of my LLM projects. A few others I've built around agents and LLM systems:

- **[CoreCoder](https://github.com/he-yufeng/CoreCoder)** — want to understand how a coding agent really works? Read the whole ~1k-line engine end to end, not a black box.
- **[RepoWiki](https://github.com/he-yufeng/RepoWiki)** — dropped into an unfamiliar codebase? It gives you a guided wiki and a where-to-start reading path, a self-hostable DeepWiki alternative.
- **[FindJobs-Agent](https://github.com/he-yufeng/FindJobs-Agent)** — stop sifting job boards by hand: it ranks postings against your resume and runs mock interviews.

## License

MIT — see [LICENSE](LICENSE).
