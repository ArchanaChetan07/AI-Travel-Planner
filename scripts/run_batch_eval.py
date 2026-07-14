"""Batch eval CLI — see src.eval.batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.eval.batch import DEFAULT_REQUESTS, run_batch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DEMO_MODE batch metrics for travel agent loop")
    parser.add_argument("--n", type=int, default=40)
    parser.add_argument("--outdir", type=Path, default=Path("artifacts"))
    args = parser.parse_args(argv)

    requests = DEFAULT_REQUESTS[: max(1, min(args.n, len(DEFAULT_REQUESTS)))]
    report = run_batch(requests)
    args.outdir.mkdir(parents=True, exist_ok=True)
    out = args.outdir / "batch_metrics.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = {k: report[k] for k in report if k != "results"}
    print(json.dumps(summary, indent=2))
    print(f"Wrote {out.as_posix()}")
    return 0 if report["error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
