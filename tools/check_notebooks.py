"""Repo lint for workshop notebooks. Run: python3 scratch/check_notebooks.py"""
import ast
import json
import pathlib
import re
import sys

REPO = "langchain-samples/lc-colab-workshops"
ALLOW_NO_CLOSING = {"00_setup"}


def lint_code(source: str):
    """Parse a code cell, neutralising IPython magics and shell escapes."""
    if source.lstrip().startswith(("%%writefile", "%%bash", "%%capture")):
        return None
    lines, cont = [], False
    for ln in source.splitlines():
        stripped = ln.lstrip()
        if cont or stripped.startswith(("!", "%")):
            cont = ln.rstrip().endswith("\\")
            lines.append("pass")
            continue
        lines.append(ln)
    try:
        ast.parse("\n".join(lines))
    except SyntaxError as e:
        return f"line {e.lineno}: {e.msg}"
    return None


def main() -> int:
    nbs = sorted(pathlib.Path("notebooks").glob("*.ipynb"))
    failures, shots, total_cells = [], [], 0

    for p in nbs:
        nb = json.loads(p.read_text())
        cells = nb["cells"]
        total_cells += len(cells)
        src = "".join("".join(c["source"]) for c in cells)
        problems = []

        if any(c.get("outputs") for c in cells):
            problems.append("committed outputs")
        if f"colab.research.google.com/github/{REPO}/blob/main/notebooks/{p.stem}.ipynb" not in src:
            problems.append("missing/incorrect Colab badge")
        if re.search(r"lsv2_(sk|pt)_[A-Za-z0-9]{8,}", src) or "sk-proj-" in src:
            problems.append("LEAKED API KEY")
        for k in re.findall(r'os\.environ\["((?:OPENAI|ANTHROPIC|TAVILY)_API_KEY)"\]\s*=', src):
            problems.append(f"sets {k} (only LANGSMITH_API_KEY allowed)")
        if p.stem not in ALLOW_NO_CLOSING:
            if "📌 Key takeaways" not in src:
                problems.append("no takeaways block")
            if "🧠 Checkpoint" not in src:
                problems.append("no checkpoint")
        for i, c in enumerate(cells):
            if c["cell_type"] != "code":
                continue
            err = lint_code("".join(c["source"]))
            if err:
                problems.append(f"syntax in code cell {i}: {err}")

        shots += re.findall(r"📸 \*\*`([^`]+)`\*\*", src)
        checks = src.count("🧠 Checkpoint")
        print(f"  {p.name:34} {len(cells):3} cells  {checks} checkpoints  "
              f"{'FAIL: ' + '; '.join(problems) if problems else 'ok'}")
        if problems:
            failures.append(p.name)

    print(f"\n{len(nbs)} notebooks, {total_cells} cells, {len(shots)} screenshot placeholders")
    if shots:
        print("\nScreenshots still to capture:")
        for s in shots:
            print(f"  [ ] assets/screenshots/{s}")
    print("\nRESULT:", "ALL PASS" if not failures else f"{len(failures)} FAILING: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
