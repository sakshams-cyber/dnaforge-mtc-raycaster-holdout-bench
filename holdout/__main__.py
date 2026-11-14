"""Command line.

  python -m holdout analyze FILE [--extractor heuristic|anthropic] [--json out.json] [--memo out.md]
  python -m holdout bench make --base FILE [--base FILE ...] [--per-op 3]
  python -m holdout bench run --agent holdout|holdout-noverify|baseline|null [--workers 4]
  python -m holdout bench score
  python -m holdout serve [--port 8000]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="holdout")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze")
    a.add_argument("file")
    a.add_argument("--extractor", default=None)
    a.add_argument("--json", default=None)
    a.add_argument("--memo", default=None)

    b = sub.add_parser("bench")
    bsub = b.add_subparsers(dest="bcmd", required=True)
    bm = bsub.add_parser("make")
    bm.add_argument("--base", action="append", required=True)
    bm.add_argument("--per-op", type=int, default=3)
    br = bsub.add_parser("run")
    br.add_argument("--agent", default="holdout")
    br.add_argument("--workers", type=int, default=4)
    bsub.add_parser("score")

    s = sub.add_parser("serve")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)

    args = ap.parse_args(argv)

    if args.cmd == "analyze":
        from .pipeline import analyze_path

        rep = analyze_path(args.file, extractor=args.extractor)
        if args.json:
            Path(args.json).write_text(json.dumps(rep.to_dict(), indent=2, default=str))
        if args.memo:
            Path(args.memo).write_text(rep.memo_markdown)
        print(rep.memo_markdown)
        return 0

    if args.cmd == "bench":
        from .bench import harness

        if args.bcmd == "make":
            made = harness.make(args.base, per_op=args.per_op)
            print(f"made {len(made)} tasks in {harness.OUT / 'tasks'}")
        elif args.bcmd == "run":
            d = harness.run(args.agent, workers=args.workers)
            print(f"wrote runs to {d}")
        else:
            res = harness.score()
            print(harness.to_markdown(res))
        return 0

    if args.cmd == "serve":
        from .server import serve

        serve(args.host, args.port)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
