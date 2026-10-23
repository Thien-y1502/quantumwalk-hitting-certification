#!/usr/bin/env python3
"""Compare regenerated results/ against a reference copy (a git revision or a directory).

Tolerance policy
  * Non-float columns (families, marks, iteration counts, convergence and coverage flags)
    must match exactly.
  * Float columns must satisfy |new - ref| <= atol + rtol * |ref|. The defaults absorb the
    floating-point drift seen across operating systems and BLAS builds (observed maximum
    relative drift between Linux and Windows runs: 2.4e-7).
  * Solver residual columns (names ending in "residual") only record how well a linear
    system was solved; they are compared with the absolute tolerance --residual-atol.
  * In results/audits/run_audit.json every key except "environment" is compared the same way.

Exit status is 0 when everything matches and 1 otherwise.
"""
from __future__ import annotations
import argparse, io, json, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV_DIRS = ["results/raw", "results/tables"]
AUDIT = "results/audits/run_audit.json"


def read_ref(rel: str, ref_git: str | None, ref_dir: Path | None) -> bytes:
    if ref_git:
        return subprocess.check_output(["git", "show", f"{ref_git}:{rel}"], cwd=ROOT)
    return (ref_dir / rel).read_bytes()


def close(x: np.ndarray, y: np.ndarray, rtol: float, atol: float) -> tuple[bool, float]:
    if not np.array_equal(np.isnan(x), np.isnan(y)):
        return False, float("nan")
    m = ~np.isnan(x)
    if not m.any():
        return True, 0.0
    ok = np.allclose(x[m], y[m], rtol=rtol, atol=atol)
    # Report relative drift only for finite values well above the absolute-tolerance noise level.
    xs, ys = x[m], y[m]
    big = np.isfinite(xs) & np.isfinite(ys) & (np.abs(ys) > 1e3 * atol)
    worst = float((np.abs(xs[big] - ys[big]) / np.abs(ys[big])).max()) if big.any() else 0.0
    return bool(ok), worst


def compare_frames(new: pd.DataFrame, ref: pd.DataFrame, args) -> tuple[bool, float, str]:
    if list(new.columns) != list(ref.columns):
        return False, float("nan"), "column mismatch"
    if len(new) != len(ref):
        return False, float("nan"), f"row count {len(new)} != {len(ref)}"
    worst = 0.0
    for c in new.columns:
        a, b = new[c], ref[c]
        if pd.api.types.is_float_dtype(a) or pd.api.types.is_float_dtype(b):
            if c.endswith("residual"):
                ok, w = close(a.to_numpy(float), b.to_numpy(float), 0.0, args.residual_atol)
                w = 0.0
            else:
                ok, w = close(a.to_numpy(float), b.to_numpy(float), args.rtol, args.atol)
            worst = max(worst, w)
            if not ok:
                return False, worst, f"numeric drift in {c}"
        elif not (a.astype(str).to_numpy() == b.astype(str).to_numpy()).all():
            return False, worst, f"values differ in {c}"
    return True, worst, "ok"


def compare_audit(ref_bytes: bytes, args) -> tuple[bool, str]:
    new = json.loads((ROOT / AUDIT).read_text(encoding="utf-8"))
    ref = json.loads(ref_bytes)
    for k in sorted(set(new) | set(ref)):
        if k == "environment":
            continue
        if k not in new or k not in ref:
            return False, f"key {k} missing"
        a, b = new[k], ref[k]
        if isinstance(b, float) and not isinstance(b, bool):
            tol = (0.0, args.residual_atol) if "residual" in k else (args.rtol, args.atol)
            if not np.isclose(a, b, rtol=tol[0], atol=tol[1]):
                return False, f"{k}: {a} != {b}"
        elif a != b:
            return False, f"{k}: {a} != {b}"
    return True, "ok"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ref-git", help="git revision holding the reference results, e.g. v0.1.0")
    g.add_argument("--ref-dir", type=Path, help="directory holding a reference copy of results/")
    ap.add_argument("--rtol", type=float, default=1e-6)
    ap.add_argument("--atol", type=float, default=1e-8)
    ap.add_argument("--residual-atol", type=float, default=1e-6)
    ap.add_argument("--json", type=Path, help="also write the report as JSON")
    args = ap.parse_args()

    rows = []
    for d in CSV_DIRS:
        for f in sorted((ROOT / d).glob("*.csv")):
            rel = f"{d}/{f.name}"
            ref = pd.read_csv(io.BytesIO(read_ref(rel, args.ref_git, args.ref_dir)))
            ok, worst, msg = compare_frames(pd.read_csv(f), ref, args)
            rows.append({"file": rel, "match": ok, "max_rel_drift": worst, "note": msg})
    ok, msg = compare_audit(read_ref(AUDIT, args.ref_git, args.ref_dir), args)
    rows.append({"file": AUDIT, "match": ok, "max_rel_drift": 0.0, "note": msg})

    for r in rows:
        print(f"{'OK  ' if r['match'] else 'FAIL'} {r['file']:52s} max_rel_drift={r['max_rel_drift']:.2e}  {r['note']}")
    all_ok = all(r["match"] for r in rows)
    print(f"\n{sum(r['match'] for r in rows)}/{len(rows)} files match "
          f"(rtol={args.rtol}, atol={args.atol}, residual_atol={args.residual_atol})")
    if args.json:
        args.json.write_text(json.dumps({"reference": args.ref_git or str(args.ref_dir), "rtol": args.rtol,
                                         "atol": args.atol, "residual_atol": args.residual_atol,
                                         "all_match": all_ok, "files": rows}, indent=2), encoding="utf-8")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
