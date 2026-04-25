from __future__ import annotations
import argparse
from .pipeline import build_knowledge_graph


def main() -> None:
    p = argparse.ArgumentParser(description="Baue einen Knowledge Graph aus PDF/Markdown-Exzerpten.")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("inputs", nargs="+")
    b.add_argument("--out", required=True)
    b.add_argument("--format", choices=["svelte", "json", "graphml"], default="svelte")
    args = p.parse_args()

    if args.cmd == "build":
        kg = build_knowledge_graph(args.inputs)
        if args.format in {"svelte", "json"}:
            kg.export_json(args.out)
        else:
            kg.export_graphml(args.out)
        print(f"Wissensgraph geschrieben: {args.out}")

if __name__ == "__main__":
    main()
