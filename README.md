# gta6-twitch-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/zurrrtzy-create/gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/zurrrtzy-create/gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

A forecaster for Grand Theft Auto VI's launch-day Twitch audience: given
everything recorded up to the end of the release day's first hour, it
predicts the concurrent viewers in the "Grand Theft Auto VI" Twitch
category for each of hours 2–24 (UTC), as five quantiles (5%, 25%, 50%,
75%, 95%) per hour. The method is a similarity-weighted look at 38 past
big game launches: each past launch donates its release-day shape, weighted
by how close its first hour was to this launch's first hour, because how a
launch day unfolds depends strongly on how big its first hour was. Full
method, validation numbers and sources: [METHOD.md](METHOD.md).

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=<kit>/input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3.13, standard library only, no network) reads every
`*.in` case in the input directory and writes one `<id>.out` forecast per
case to the output directory. It runs in under a second for the four
practice cases, is deterministic (two runs write identical bytes), and
needs no arguments: with the environment variables unset it reads `/input`
and writes `/output`, as the grader runs it.

---

<sub>Entered on [make.fun](https://make.fun/?ref=2ehgyxhw&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
