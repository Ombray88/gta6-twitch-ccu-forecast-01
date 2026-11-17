"""gta6-twitch-ccu-forecast-01 entry in Python 3.13 (standard library only)."""

import json
import math
import os
import statistics
import sys
from pathlib import Path

# The grader's -P leaves /bot off sys.path: put it back first.
sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.6448536269514722, -0.6744897501960817, 0.0, 0.6744897501960817, 1.6448536269514722]


def round2(x: float) -> float | int:
    """x rounded to 2 decimals, half up, as JavaScript's Math.round(x * 100) / 100 rounds it."""
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if value.is_integer() else value


def extract_comp_hours(comp: dict) -> list[float] | None:
    ds = comp.get("day_start")
    if not ds or len(ds) < 10:
        return None
    ds_date = ds[:10]
    by_hour = {}
    for pt in comp.get("hourly", []):
        f = pt.get("from", "")
        if f.startswith(ds_date):
            try:
                h = int(f[11:13]) + 1
                if 1 <= h <= 24:
                    by_hour[h] = float(pt["viewers"])
            except (ValueError, IndexError):
                pass
    if len(by_hour) < 24:
        return None
    hrs = [by_hour[h] for h in range(1, 25)]
    if hrs[0] <= 0:
        return None
    return hrs


def filter_comparables(comparables: list[dict]) -> list[list[float]]:
    all_valid = []
    for comp in comparables:
        hrs = extract_comp_hours(comp)
        if hrs is not None:
            all_valid.append((comp, hrs))

    filtered = []
    for comp, hrs in all_valid:
        p1 = hrs[0]
        if p1 < 5000:
            continue
        unlock = str(comp.get("unlock", "")).lower()
        if "early-access-contaminated" in unlock or "f2p" in unlock or "free-to-play" in unlock:
            continue
        if "simultaneous" in unlock and "rolling" not in unlock:
            continue
        if "pc" in unlock and ("simultaneous" in unlock or "single global" in unlock):
            continue
        filtered.append(hrs)

    rolling_subset = []
    for comp, hrs in all_valid:
        p1 = hrs[0]
        if p1 < 5000:
            continue
        unlock = str(comp.get("unlock", "")).lower()
        if "early-access-contaminated" in unlock or "f2p" in unlock or "free-to-play" in unlock:
            continue
        if "pc" in unlock and ("simultaneous" in unlock or "single global" in unlock):
            continue
        if "rolling" in unlock or "midnight local" in unlock:
            rolling_subset.append(hrs)

    if len(rolling_subset) >= 8:
        pool = rolling_subset
    else:
        pool = filtered

    if len(pool) < 5:
        pool = [hrs for _, hrs in all_valid]

    if len(pool) < 5:
        return []

    return pool


def forecast_case(case: dict, name: str) -> dict:
    if case.get("levels") != LEVELS:
        raise ValueError(f"{name} asks for levels {case.get('levels')}, not {LEVELS}")
    first = next((k for k in case.get("known", []) if k.get("hour") == 1), None)
    if first is None:
        raise ValueError(f"{name} has no hour-1 print")
    p1 = max(1.0, float(first["viewers"]))

    comparables = case.get("comparables", [])
    pool = filter_comparables(comparables)

    hours_out = []
    for h in range(2, 25):
        if len(pool) >= 1:
            lrs = []
            for hrs in pool:
                v1 = hrs[0]
                vh = hrs[h - 1]
                if v1 > 0 and vh > 0:
                    lrs.append(math.log(vh / v1))
            if len(lrs) >= 1:
                center = statistics.median(lrs)
                sd = statistics.pstdev(lrs) if len(lrs) > 1 else 0.15 * math.sqrt(h - 1)
                sd = max(0.10, min(0.90, sd))
            else:
                center = 0.0
                sd = 0.15 * math.sqrt(h - 1)
        else:
            center = 0.0
            sd = 0.15 * math.sqrt(h - 1)

        row = []
        prev = 0.0
        for z in Z:
            val = p1 * math.exp(center + z * sd)
            r = round2(val)
            c = max(1, min(1000000000, r))
            if c < prev:
                c = prev
            row.append(c)
            prev = c
        hours_out.append({"hour": h, "q": row})

    return {"hours": hours_out}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case, path.name)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(
            json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
