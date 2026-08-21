<!--
Ticket draft for langchain-ai/langchain -> New issue -> "🐛 Bug Report".

Everything below the line is the ISSUE BODY, in the exact shape the form renders:
one `###` heading per field, in template order, with every checkbox option listed.
Paste it whole after submitting the blank form, or fill the fields to match.

ISSUE TITLE (separate field, not part of the body):
`[` or `]` in a node name makes `draw_mermaid_png()` fail with a 400
-->

### Submission checklist

- [x] This is a bug, not a usage question.
- [x] I added a clear and descriptive title that summarizes this issue.
- [x] I used the GitHub search to find a similar question and didn't find it.
- [x] I am sure that this is a bug in LangChain rather than my code.
- [x] The bug is not resolved by updating to the latest stable version of LangChain (or the specific integration package).
- [x] This is not related to the langchain-community package.
- [x] I posted a self-contained, minimal, reproducible example. A maintainer can copy it and run it AS IS.

### Package (Required)

- [x] langchain
- [ ] langchain-openai
- [ ] langchain-anthropic
- [ ] langchain-classic
- [x] langchain-core
- [ ] langchain-model-profiles
- [ ] langchain-tests
- [ ] langchain-text-splitters
- [ ] langchain-chroma
- [ ] langchain-deepseek
- [ ] langchain-exa
- [ ] langchain-fireworks
- [ ] langchain-groq
- [ ] langchain-huggingface
- [ ] langchain-mistralai
- [ ] langchain-nomic
- [ ] langchain-ollama
- [ ] langchain-openrouter
- [ ] langchain-perplexity
- [ ] langchain-qdrant
- [ ] langchain-xai
- [ ] Other / not sure / general

### Related Issues / PRs

* #32857 introduced `_to_safe_id`, which is where this regression comes from. It replaced
  `_escape_node_label` to fix node-id *collisions* (`_escape_node_label("开")` and
  `_escape_node_label("始")` both returned `'_'`). The replacement produces unique ids, but ids
  Mermaid cannot parse.
* #34444 and #30427 report the same 400 symptom from different causes (`bgColor` not
  URL-encoded, fixed in #34461). Not duplicates of this one — node names there contain no
  special characters.

### Reproduction Steps / Example Code (Python)

```python
from typing import TypedDict

from langchain_core.runnables.graph_mermaid import _to_safe_id
from langgraph.graph import END, START, StateGraph


class S(TypedDict):
    x: int


def build(node_name: str):
    g = StateGraph(S)
    g.add_node(node_name, lambda s: s)
    g.add_edge(START, node_name)
    g.add_edge(node_name, END)
    return g.compile()


# "Plain.before_model" renders. "PIIMiddleware[email].before_model" raises.
for name in ["Plain.before_model", "PIIMiddleware[email].before_model"]:
    print(name, "->", _to_safe_id(name))
    try:
        build(name).get_graph().draw_mermaid_png()
        print("   draw_mermaid_png: OK")
    except Exception as e:
        print(f"   draw_mermaid_png: {type(e).__name__}: {str(e).splitlines()[0]}")
```

### Error Message and Stack Trace (if applicable)

```shell
Plain.before_model -> Plain\2ebefore_model
   draw_mermaid_png: OK
PIIMiddleware[email].before_model -> PIIMiddleware\5bemail\5d\2ebefore_model
   draw_mermaid_png: ValueError: Failed to reach https://mermaid.ink API while trying to render your graph. Status code: 400.

Traceback (most recent call last):
  File ".../langchain_core/runnables/graph.py", line 695, in draw_mermaid_png
    return draw_mermaid_png(
  File ".../langchain_core/runnables/graph_mermaid.py", line 314, in draw_mermaid_png
    img_bytes = _render_mermaid_using_api(
  File ".../langchain_core/runnables/graph_mermaid.py", line 484, in _render_mermaid_using_api
    raise ValueError(msg)
ValueError: Failed to reach https://mermaid.ink API while trying to render your graph. Status code: 400.

To resolve this issue:
1. Check your internet connection and try again
2. Try with higher retry settings: `draw_mermaid_png(..., max_retries=5, retry_delay=2.0)`
3. Use the Pyppeteer rendering method which will render your graph locally in a browser: `draw_mermaid_png(..., draw_method=MermaidDrawMethod.PYPPETEER)`
```

### Description

* I'm building agents with `PIIMiddleware`, which names its nodes `PIIMiddleware[<pii_type>]`.
* I expect `draw_mermaid_png()` to render the graph, as it does for agents built with any other
  middleware.
* Instead it raises `ValueError`. In a notebook this is worse than it sounds: leaving the compiled
  agent as a cell's last expression calls `_repr_mimebundle_()`, which calls `draw_mermaid_png()`.
  So merely *displaying* such an agent throws a traceback, even though the agent itself is fine
  and runs correctly.

The cause is `_to_safe_id()` in `libs/core/langchain_core/runnables/graph_mermaid.py`, which maps
every character outside `[A-Za-z0-9_-]` to `\` + hex codepoint:

```python
allowed = string.ascii_letters + string.digits + "_-"
out = [ch if ch in allowed else "\\" + format(ord(ch), "x") for ch in label]
```

Backslashes are not valid in a Mermaid node id. `\2e` (from `.`) happens to survive, so most
graphs render and the scheme looks correct; `\5b` / `\5d` (from `[` / `]`) does not, and Mermaid
rejects the whole document. The docstring's claim that the result is *"guaranteed to be unique and
Mermaid-compatible, so nodes with special characters always render correctly"* does not hold.

**Suggested fix.** The constraint from #32857 still applies — mapping disallowed characters to `_`
alone would reintroduce the collisions that PR fixed — so the id needs to be both Mermaid-legal
*and* unique, and the human-readable name needs to live somewhere Mermaid permits punctuation.
Mermaid's quoted label does exactly that:

```
PIIMiddleware_email_before_model["PIIMiddleware[email].before_model"]
```

Verified to render via `draw_mermaid_png()`, where the current output for the same node does not.
Concretely: sanitise the id to `[A-Za-z0-9_-]` using `_`, append a short deterministic suffix (e.g.
6 hex chars of a hash of the original label) when sanitising collides, and emit the original label
in quotes. That satisfies both constraints at once, where `_escape_node_label` satisfied only
legality and `_to_safe_id` satisfies only uniqueness. It also stops `\2e` appearing in rendered
labels on graphs that do currently render.

**Secondary.** A 400 means the document was rejected, but the error message says "Failed to reach"
and all three suggested remedies concern connectivity or the rendering backend. Distinguishing 4xx
from connection errors and 5xx in `_render_mermaid_using_api` would point at the real cause.

Note `PIIMiddleware.name` is a read-only `@property` returning
`f"{self.__class__.__name__}[{self.pii_type}]"`, so there is no caller-side workaround short of
subclassing.

### System Info

System Information
------------------
> OS:  Darwin
> OS Version:  Darwin Kernel Version 25.5.0: Tue Jun  9 22:28:34 PDT 2026; root:xnu-12377.121.10~1/RELEASE_ARM64_T6050
> Python Version:  3.14.6 (main, Jun 23 2026, 15:46:31) [Clang 22.1.3 ]

Package Information
-------------------
> langchain_core: 1.6.0
> langsmith: 0.11.1
> langchain_protocol: 0.0.18
> langgraph_sdk: 0.4.3

Optional packages not installed
-------------------------------
> deepagents
> deepagents-cli

Other Dependencies
------------------
> anyio: 4.14.2
> distro: 1.9.0
> httpx: 0.28.1
> jsonpatch: 1.33
> orjson: 3.12.0
> packaging: 26.3
> pydantic: 2.13.4
> pyyaml: 6.0.3
> requests: 2.34.2
> requests-toolbelt: 1.0.0
> sniffio: 1.3.1
> tenacity: 9.1.4
> typing-extensions: 4.16.0
> uuid-utils: 0.17.0
> websockets: 16.1.1
> xxhash: 4.0.1
> zstandard: 0.25.0

### Social handles (optional)

