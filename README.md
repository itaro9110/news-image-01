# The World in One Page — 20 Stories

A one-page newspaper front page summing up Friday 13 November 2026:
20 verified stories in a 5-column by 4-row grid, each with a region
tag, a hand-drawn pictogram, a two-line headline and a two-line
sub-label. The top stories: NVIDIA CEO Jensen Huang resigns, the
DOJ moves to seize $1.2B in the Binance hack, a worldwide Microsoft
outage, Iran's radar claim in the Gulf (labelled as a claim, not
verified), a tanker hitting a mine in Hormuz, and Europe joining the
Ukraine peace talks.

## How it is drawn

`main.py` (Python 3, standard library only) draws everything
procedurally: a hand-rolled PNG encoder, a small canvas with rect /
circle / line / triangle primitives, a 5x7 bitmap font, and twenty
small pictogram functions. No image assets, no network, no clock —
two runs produce byte-identical output.

## Why 20 stories

The leading entries are 16-story front pages. Twenty stories is the
differentiator: the same day, wider breadth — Middle East, Europe,
business, crypto, tech, the US, the Americas and Asia, with the
second-tier stories (Storm Charles, the Sri Lanka budget, the
Bangladesh garment dispute) that a 16-story page has to drop.
Headlines are kept to 16 characters a line so they stay legible at
300 pixels across, and every unverified claim is labelled as one.

## Run

```
python3 main.py
```

Writes `entry.png` (1024x1024) to `$MAKEFUN_OUTPUT_DIR`, else
`/output` when it exists and is writable, else `/tmp`.
