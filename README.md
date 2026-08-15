# LangChain & LangSmith Workshops

Hands-on notebooks for learning to build agents with **Deep Agents** and to evaluate them with
**LangSmith**. Every lesson opens in Google Colab and runs top to bottom.

The teaching approach is **whole game first**: lesson 01 builds a working research agent in
about ten lines of code, and the lessons after it take that agent apart one layer at a time.
No theory before anything runs.

## Before you start

You need **one** thing: a [LangSmith API key](https://smith.langchain.com). No OpenAI key, no
Anthropic key, no credit card, nothing installed locally — models are served through the
LangSmith gateway, so a single key covers models, tracing, and Studio for all 15 notebooks.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/langchain-samples/lc-colab-workshops/blob/main/notebooks/00_setup.ipynb)
 **Start here → [00 · Setup and preflight](notebooks/00_setup.ipynb)**

Run it a few days before the workshop, not on the morning of. It checks five things and tells
you exactly what to fix if any of them fail — and one of the checks can fail for reasons only a
workspace admin can resolve.

## Part 1 — Building agents

| | Lesson | You build | Key ideas |
|---|---|---|---|
| 01 | [The whole game](notebooks/01_first_deep_agent.ipynb) | a research assistant | `create_deep_agent`, the harness, tracing, Studio |
| 02 | [Files as a workspace](notebooks/02_backends.ipynb) | the same agent, four ways | context offloading, `State`/`Store`/`Filesystem`/`Composite` backends |
| 03 | [Tools](notebooks/03_tools.ipynb) | a customer support agent | `@tool`, docstrings as prompts, error messages, return shape |
| 04 | [MCP servers](notebooks/04_mcp.ipynb) | a docs search agent | `MultiServerMCPClient`, tool budgets, untrusted tool text |
| 05 | [Subagents](notebooks/05_subagents.ipynb) | a research team | context isolation, per-subagent tools and models |
| 06 | [Middleware & HITL](notebooks/06_middleware_and_hitl.ipynb) | a production support agent | retries, summarization, PII, custom middleware, approvals |
| 07 | [Memory](notebooks/07_memory.ipynb) | an assistant that learns | `AGENTS.md`, `/memories/`, namespaces, per-user scoping |
| 08 | [Skills](notebooks/08_skills.ipynb) | a report writer | `SKILL.md`, progressive disclosure, bundled files |
| 09 | [Under the hood](notebooks/09_under_the_hood.ipynb) | *(nothing new)* | `create_agent` equivalence, LangGraph, checkpointers, time travel |

## Part 2 — Evaluating agents

The organising analogy: **single step ≈ unit test, trajectory ≈ integration test, final response
≈ end-to-end test.**

| | Lesson | You build | Key ideas |
|---|---|---|---|
| 10 | [From vibes to a test suite](notebooks/10_evals_from_traces.ipynb) | your first dataset | traces → datasets, `evaluate()`, comparing experiments |
| 11 | [Unit tests for agents](notebooks/11_single_step_evals.ipynb) | calibrated judges | `exact_match`, JSON match, LLM-as-judge, **calibration** |
| 12 | [Integration tests](notebooks/12_trajectory_evals.ipynb) | trajectory metrics | match modes, tool-args matching, trajectory judges |
| 13 | [Evals in CI](notebooks/13_evals_in_ci.ipynb) | a pytest suite + Actions | merge gates vs nightly, baselines, cost budgets |
| 14 | [Online evals](notebooks/14_online_evals.ipynb) | a production loop | run rules, annotation queues, closing the loop |

## How the notebooks work

- **Self-contained.** Each notebook creates everything it needs. No cloning, no downloads, no
  imports from this repo — open the `.ipynb` in Colab, add one secret, run.
- **Standalone.** Lessons build on each other conceptually but not technically. You can open
  lesson 07 without having run 01–06.
- **Checkpoints.** Each lesson has questions with hidden answers. Several can only be answered
  by reading a trace in LangSmith, which is deliberate.
- **One exercise each**, with a solution inline behind a toggle.

## Running locally

Colab is the intended environment, but the notebooks work in any Jupyter setup:

```bash
uv venv && source .venv/bin/activate
uv pip install deepagents~=0.7.6 langchain~=1.3.15 langchain-openai~=1.5.1 langsmith~=0.11.0
export LANGSMITH_API_KEY=lsv2_...
jupyter lab
```

The setup cell falls back to reading `LANGSMITH_API_KEY` from the environment when
`google.colab` is unavailable. File paths are relative, so they resolve the same way in both
places.

## For maintainers

```bash
uv sync --group dev && uv run lefthook install
```

Git hooks then strip notebook outputs, run Ruff and ty, lint every notebook, and scan
for credentials on each commit. See [CONTRIBUTING.md](CONTRIBUTING.md) for the notebook conventions.
