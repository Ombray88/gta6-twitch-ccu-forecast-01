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


def _is_gta_like(comp: dict, hrs: list[float]) -> bool:
    """Determine whether a comparable launch serves as a valid GTA VI analogue.

    A comparable is a good GTA VI analogue when it is a rolling-midnight
    console launch (no simultaneous PC unlock that would make hour 1 the
    global peak), not early-access contaminated, not free-to-play, and
    its hour-1 print is at least 5000 viewers.
    """
    if not hrs or hrs[0] < 5000:
        return False
    notes = str(comp.get("unlock", "")).lower()
    if "early-access-contaminated" in notes or "f2p" in notes or "free-to-play" in notes:
        return False
    # Note: general "simultaneous" check is omitted because the word is unreliable
    # (e.g. Zelda is rolling-midnight yet mentions "simultaneous" for NA), and
    # the PC rule below already excludes problematic simultaneous-global launches.
    if "pc" in notes and ("simultaneous" in notes or "single global" in notes):
        return False
    return True


def filter_comparables(comparables: list[dict]) -> list[list[float]]:
    extracted = []
    for candidate in comparables:
        sequence = extract_comp_hours(candidate)
        if sequence is not None:
            extracted.append((candidate, sequence))

    standard_pool = [seq for candidate, seq in extracted if _is_gta_like(candidate, seq)]

    rolling_pool = []
    for candidate, seq in extracted:
        if _is_gta_like(candidate, seq):
            details = str(candidate.get("unlock", "")).lower()
            if "rolling" in details or "midnight local" in details:
                rolling_pool.append(seq)

    active_pool = rolling_pool if len(rolling_pool) >= 8 else standard_pool

    if len(active_pool) < 5:
        active_pool = [seq for _, seq in extracted]

    if len(active_pool) < 5:
        return []

    return active_pool


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
    lp = math.log(p1)
    for h in range(2, 25):
        if len(pool) >= 1:
            pairs = []
            lrs = []
            for hrs in pool:
                v1_comp = hrs[0]
                vh = hrs[h - 1]
                if v1_comp > 0 and vh > 0:
                    lr = math.log(vh / v1_comp)
                    lrs.append(lr)
                    w = math.exp(-0.5 * ((math.log(v1_comp) - lp) / 1.0) ** 2)
                    pairs.append((lr, w))
            if len(pairs) >= 1:
                sorted_pairs = sorted(pairs, key=lambda x: x[0])
                total_w = sum(w for _, w in sorted_pairs)
                cum_w = 0.0
                half_w = total_w / 2.0
                center = sorted_pairs[-1][0]
                for lr, w in sorted_pairs:
                    cum_w += w
                    if cum_w >= half_w:
                        center = lr
                        break
                sd = statistics.pstdev(lrs) if len(lrs) > 1 else 0.15 * math.sqrt(h - 1)
                sd = max(0.15, min(0.90, sd))
            else:
                center = 0.0
                sd = 0.15 * math.sqrt(h - 1)
        else:
            center = 0.0
            sd = 0.15 * math.sqrt(h - 1)

        if h <= 2:
            bias = 0.0
        elif h < 6:
            bias = 0.35 * (h - 2) / 4.0
        else:
            bias = 0.35

        row = []
        prev = 0.0
        for z in Z:
            val = p1 * math.exp(center + bias + z * sd)
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
