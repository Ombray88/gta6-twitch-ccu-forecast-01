# gta6-twitch-ccu-forecast-01

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Ombray88/gta6-twitch-ccu-forecast-01/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Ombray88/gta6-twitch-ccu-forecast-01/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

This program forecasts hour-by-hour concurrent Twitch viewers for Grand Theft Auto VI on its launch day (hours 2..24) across five quantiles, derived from the comparables' unlock-wave median log-ratios.

## Run it
```bash
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## The Model
- Extracts release-day hourly viewer curves from comparable big game launches, filtering for console/rolling midnight unlocks and robust viewer scales.
- Computes log-ratios relative to hour 1 across the comparable pool, taking the median center and population standard deviation (floored at 0.10, capped at 0.90) for each hour 2..24.
- Quantiles are projected via log-normal scaling around hour 1's print (`p1 * exp(center + z * sd)`), rounded half-up to 2 decimals, clamped to `[1, 1e9]`, and enforced non-decreasing.

<sub>Entered on [make.fun](https://make.fun/?ref=9w5z28cm&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
