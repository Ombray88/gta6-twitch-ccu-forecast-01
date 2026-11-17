# GTA VI Twitch Viewers Forecast (gta6-twitch-ccu-forecast-01)

## What the Program Does
Forecasts hour-by-hour concurrent Twitch viewers (CCU) for Grand Theft Auto VI on its launch day (hours 2..24) at five quantile levels `[0.05, 0.25, 0.5, 0.75, 0.95]`, reading case input JSON from `MAKEFUN_INPUT_DIR` (default `/input`) and writing quantile predictions to `MAKEFUN_OUTPUT_DIR` (default `/output`).

## How to Run
```bash
mkdir -p out
MAKEFUN_INPUT_DIR=gta6-twitch-ccu-forecast-01-kit/input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## The Model
- Extracts release-day hourly viewer curves from comparable big game launches, filtering for console/rolling midnight unlocks and robust viewer scales.
- Computes log-ratios relative to hour 1 across the comparable pool, taking the median center and population standard deviation (floored at 0.10, capped at 0.90) for each hour 2..24.
- Quantiles are projected via log-normal scaling around hour 1's print (`p1 * exp(center + z * sd)`), rounded half-up to 2 decimals, clamped to `[1, 1e9]`, and enforced non-decreasing.
