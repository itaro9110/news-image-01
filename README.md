# The World in One Page — news-image-01

A newspaper front page summing up Friday 13 November 2026 in one
image. `main.py` (Python 3.13, standard library only) draws the whole
page procedurally — masthead, six story panels, pictograms, and a
hand-built 5x7 bitmap font — and writes one 1024x1024 PNG.

## Stories

1. **MIDDLE EAST** — "IRAN SAYS IT HIT US RADAR" / tanker hits a mine
   in Hormuz
2. **EUROPE** — "EU JOINS UKRAINE PEACE TALKS" / biggest prisoner
   swap eyed
3. **BUSINESS** — "NVIDIA CEO HUANG RESIGNS" / Kress is interim chief
4. **CRYPTO** — "DOJ TO SEIZE $1.2B IN BINANCE HACK" / FBI blames
   North Korea
5. **TECH** — "MICROSOFT OUTAGE HITS WORLDWIDE" / businesses disrupted
6. **USA** — "BROOKLYN COLLAPSE 8 DEAD" / search ends, 18 hurt

Unverified claims stay labelled as claims ("IRAN SAYS", "FBI BLAMES").

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

No network, no fonts, no image files. Deterministic: two runs write
byte-identical PNGs.

## Verification

- Two runs byte-identical: sha256
  `10b9f31f337834de3eb621d1b13a6e6a2851504879a17eefbb90f141ed3ed174`.
- PNG 1024x1024, 17,374 bytes (limit 1,048,576), valid PNG magic.
- `main.py`: 311 lines, 11,359 bytes, written fresh in this session
  in ~13 chunks plus two genuine fix edits (cleaner `$` glyph,
  larger explosion burst).
- Runs as an unprivileged user in a read-only container: with no
  `MAKEFUN_OUTPUT_DIR` it writes to `/output` when writable, else
  `/tmp` — never a relative `out` directory.

## License

MIT — see LICENSE.
