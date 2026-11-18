# Method note — GTA VI launch-day Twitch forecast

## What is being forecast

Grand Theft Auto VI releases 19 November 2026 on PlayStation 5 and Xbox
Series X|S, rolling midnight local time (New Zealand first at 11:00 UTC
18 Nov; UK 00:00 UTC; US East 05:00 UTC; US West 08:00 UTC), no PC at
launch. The counted quantity is Twitch's concurrent viewers in the
"Grand Theft Auto VI" category (Twitch game id 1867279146), one print per
hour = the mean of that hour's valid minute reads. `main.py` reads one case
(everything recorded up to the end of hour 1, that hour's print included)
and writes five quantiles (5/25/50/75/95%) of each of hours 2–24.

Sources: the competition's own kit and rules (unlock times, Twitch game id,
the recorder's method); Rockstar Support / PlayStation statements on the
rolling-midnight launch (confirmed by press coverage 17–18 Nov 2026);
SullyGnome.com hourly Twitch category averages, which the case files ship
as the comparables' data.

## The model

For each comparable launch, take its release-day hourly curve as ratios to
its own hour-1 print. For the case at hand, weight each comparable by a
Gaussian kernel on the log distance between its hour-1 print and the case's
hour-1 print (bandwidth 1.0 in log units). For each hour, the forecast
quantiles are the weighted quantiles of the donors' log-ratios, shrunk 0.85
of the way toward the weighted median.

Why this shape: across the 38 donors, log(hour-1 viewers) correlates
**-0.94** with log(peak / hour-1). A launch whose first hour is huge is
already near its peak; a launch whose first hour is small typically grows
several-fold as time zones unlock and the US wakes up. The median donor
profile dips to ~0.73× hour 1 in hours 3–5, then climbs to ~2.4× by hour
19–20. The kernel lets the forecast's shape adapt to the launch's size
instead of imposing one average curve: at an hour-1 print of 800k the
weighted-median peak is ~1.2×, at 100k it is ~1.7×.

## Validation — leave-one-out over the 38 comparables

Each comparable in turn played the target (hour 1 known, the other 37 as
donors); scored by the contest's own pinball loss on the log scale.

| model | mean loss, all 37 | mean loss, hour-1 in [50k, 1M] (20) |
|---|---|---|
| house baseline (flat at hour 1, σ=0.15) | 0.9296 | 0.2509 |
| **this model (kernel bw 1.0, spread 0.85)** | **0.4110** | **0.2036** |
| same, unweighted median | 0.7159 | — |
| same, rolling-midnight donors only | 0.8388 | — |
| same, spread ×1.0 / ×0.8 | 0.4100 / 0.4128 | 0.2051 / 0.2038 |

The house baseline's published practice loss is ~0.387; the subset column
is the regime that matters for GTA VI (its hour-1 print will be large).
The worst leave-one-out cases are simultaneous-global unlocks with a
near-empty hour 1 (Black Myth: Wukong, Hollow Knight: Silksong) — a shape
GTA VI, a rolling-midnight console launch, does not share.

## What was tried and rejected

- **Unweighted median profile**: much worse (0.72) — the tiny-hour-1
  simultaneous-unlock donors distort both the median and the spread.
- **Rolling-midnight donors only**: worse (0.84) — 12 donors are too few;
  the kernel already downweights the wrong-shaped ones.
- **Hour-1 channels-per-viewer as a second similarity dimension**: no
  gain (subset 0.205 → 0.205–0.207).
- **Pre-launch hype level** (mean viewers 24 h before release, relative
  to hour 1) as a predictor of the day's peak ratio: correlation −0.01 —
  no signal, dropped.
- **Smoothing the median across hours, spread 0.7–1.5, bandwidth
  0.5–2.0**: all within noise of the chosen values; the simplest settings
  were kept.
- **Top-20 live streams / top categories snapshots** (present only in
  the final case): deliberately unused — no leave-one-out test can vouch
  for a signal that exists in only one case.

## Limits

- The practice cases are scored by the server after submission; the
  leave-one-out numbers above are the honest pre-submission evidence.
  The final is a single case (GTA VI itself), so even a good average
  model can miss if this launch behaves unlike any donor.
- The model assumes the release-day shape is governed by launch size and
  the rolling-midnight pattern. A server outage, a delayed unlock, or a
  single mega-streamer dominating hour 1 would break that assumption;
  the quantiles carry a wide spread for exactly that reason.
- All figures are forecasts, not facts: no future viewership number in
  this repository is claimed as known.
