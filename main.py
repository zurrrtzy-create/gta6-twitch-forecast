"""Forecast Grand Theft Auto VI's launch-day Twitch viewers, hour by hour.

Method (chosen by leave-one-out testing on the 38 past launches the case
ships as comparables; see METHOD.md for the numbers):

The case gives us one anchor -- hour 1's print -- and, for every comparable
launch, its full release-day hourly curve.  Launch days differ wildly in
shape, but one fact is stable: how a launch day unfolds depends strongly on
how big its first hour was.  Across the comparables, log(hour-1 viewers)
correlates -0.94 with log(peak / hour-1): a launch whose first hour is huge
is already near its peak, while a launch whose first hour is small typically
grows several-fold as the world wakes up and the US unlocks.  So each
comparable is weighted by how close its hour-1 size is to this case's hour-1
print (a Gaussian kernel, bandwidth 1.0 in log units), and for each hour we
take the weighted quantiles of the comparables' log-ratios to their own
hour 1.  The spread is shrunk by 0.85 around the weighted median: the raw
cross-launch dispersion is slightly wider than the truth warrants, because
a few donors are simultaneous-global unlocks whose hour 1 was nearly empty.

What the program deliberately does NOT use: the case's own pre-launch
history (its level does not predict the day's shape -- correlation -0.01 in
leave-one-out), the hour-1 channels-per-viewer ratio (adding it as a second
similarity dimension did not help), and the final case's top-streams /
top-categories snapshots (they exist only in the final case, so no
leave-one-out test can vouch for them; an untested signal is a liability).

Deterministic: no clock, no randomness, no network, sorted iteration, so
two runs on one case write identical bytes.  Standard library only.
"""

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
# Bandwidth of the hour-1 similarity kernel, in natural-log units.
BANDWIDTH = 1.0
# The raw cross-launch spread is shrunk this far toward the median.
SPREAD = 0.85
# A comparable only donates its shape when its release day is this complete.
MIN_DAY_HOURS = 20
# Fallback spread (log units per sqrt hour) if no donor covers an hour.
FALLBACK_SIGMA = 0.15
Z = [-1.6448536269514722, -0.6744897501960817, 0.0,
     0.6744897501960817, 1.6448536269514722]
MAX_VIEWERS = 1_000_000_000


def parse_time(text):
    """An ISO 8601 UTC timestamp as an aware datetime."""
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def release_day_profile(comparable):
    """{hour: viewers} for the comparable's release day, hours 1-24.

    Returns an empty dict when the day is too sparse to trust: the
    target game's own pre-release history is shaped like this (its
    "release day" is a premiere day, not a launch) and is excluded by
    the same rule.
    """
    day_start = parse_time(comparable["day_start"])
    profile = {}
    for row in comparable.get("hourly", []):
        viewers = row.get("viewers")
        if not viewers or viewers <= 0:
            continue
        delta = (parse_time(row["from"]) - day_start).total_seconds() / 3600
        if delta == int(delta) and 0 <= delta < 24:
            profile[int(delta) + 1] = viewers
    if 1 not in profile or len(profile) < MIN_DAY_HOURS:
        return {}
    return profile


def weighted_quantile(pairs, tau):
    """Weighted tau-quantile of (value, weight) pairs, linearly interpolated."""
    ordered = sorted(pairs)
    total = sum(weight for _, weight in ordered)
    if total <= 0:
        return ordered[len(ordered) // 2][0]
    target = tau * total
    cumulative = 0.0
    previous_value = ordered[0][0]
    for value, weight in ordered:
        cumulative += weight
        if cumulative >= target:
            if cumulative == weight:
                return value
            fraction = (target - (cumulative - weight)) / weight
            return previous_value + fraction * (value - previous_value)
        previous_value = value
    return ordered[-1][0]


def round2(value):
    """Round half up to 2 decimals; whole numbers come back as ints."""
    scaled = value * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    rounded = whole / 100
    return int(rounded) if rounded.is_integer() else rounded


def forecast_case(case):
    if case["levels"] != LEVELS:
        raise ValueError(f"levels {case['levels']} are not {LEVELS}")
    known = next((k for k in case["known"] if k["hour"] == 1), None)
    if known is None:
        raise ValueError("case has no hour-1 print")
    first_hour = max(1, known["viewers"])
    log_first = math.log(first_hour)

    donors = []  # (log hour-1 viewers, weight, {hour: viewers})
    for comparable in case.get("comparables", []):
        profile = release_day_profile(comparable)
        if not profile:
            continue
        log_donor_first = math.log(profile[1])
        weight = math.exp(-0.5 * ((log_first - log_donor_first) / BANDWIDTH) ** 2)
        donors.append((log_donor_first, weight, profile))
    # Sort by hour-1 size only: sorting the bare tuples would compare the
    # profile dicts on a tie and raise.  The order is deterministic either
    # way (the input file's order breaks no ties that matter), this just
    # keeps it explicit and crash-proof.
    donors.sort(key=lambda donor: donor[0])

    hours = []
    for row in case["forecast"]:
        hour = row["hour"]
        pairs = []
        for _, weight, profile in donors:
            if hour in profile:
                pairs.append((math.log(profile[hour] / profile[1]), weight))
        if pairs:
            median = weighted_quantile(pairs, 0.5)
            quantiles = []
            for tau in LEVELS:
                raw = weighted_quantile(pairs, tau)
                quantiles.append(median + (raw - median) * SPREAD)
        else:
            # No donor covers this hour: fall back to a widening band
            # around the first hour's print (the house baseline's shape).
            spread = FALLBACK_SIGMA * math.sqrt(hour - 1)
            quantiles = [z * spread for z in Z]
        values = []
        for q in quantiles:
            value = round2(first_hour * math.exp(q))
            value = max(1, min(MAX_VIEWERS, value))
            values.append(value)
        # The output contract needs non-decreasing quantiles; rounding
        # can only ever tie neighbours, never invert them, but enforce it.
        for i in range(1, len(values)):
            values[i] = max(values[i], values[i - 1])
        hours.append({"hour": hour, "q": values})
    return {"hours": hours}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case)
        out = OUTPUT_DIR / f"{path.stem}.out"
        out.write_text(
            json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
