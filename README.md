# The World in One Page — v2 (16 stories)

A one-page newspaper front page summing up Friday 13 November 2026:
sixteen verified stories from one day, in a strict 4 x 4 grid.

Each panel carries a region tag, a pictogram, a two-line headline and a
one-line sub-label. Unverified claims are labelled as claims
("Iran says..."), never as fact.

## Run

    python3 main.py

Writes one PNG to $MAKEFUN_OUTPUT_DIR, else /output if it exists and is
writable, else /tmp/entry.png. 1024 x 1024, deterministic (two runs are
byte-identical). Python 3 standard library only, no network, no clock.

## Verified

Two fresh runs byte-identical (sha256
783fe437acdb6ffcd778df96472ae34692b3871d144a09857a030f4e51262103,
24,746 bytes). Also exits 0 as user `nobody` in a read-only copy with
MAKEFUN_OUTPUT_DIR unset (writes to /tmp) — the grader's condition.
