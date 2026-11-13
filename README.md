# Friday 13 November 2026 — The World in One Page

Entry for make.fun competition `news-image-01`: one image that sums
up the world's news of Friday 13 November 2026.

## What it is

A newspaper front page, drawn procedurally by `main.py` with the
Python standard library only. No image files, no fonts, no network:
every pixel is drawn from a small embedded 5x7 bitmap font.

The masthead dates the page, and six panels cover the day's most
consequential stories across regions and fields:

1. **Middle East** — Iran says it hit a US radar in Bahrain;
   a tanker hits a mine in the Strait of Hormuz.
2. **Europe** — the EU joins the Ukraine peace talks; the biggest
   prisoner swap of the war is eyed.
3. **Business** — NVIDIA CEO Jensen Huang resigns; CFO Colette
   Kress is interim chief.
4. **Crypto** — the DOJ moves to seize $1.2B in the Binance hack;
   the FBI blames North Korea.
5. **Tech** — a Microsoft outage hits businesses worldwide.
6. **USA** — the Brooklyn collapse: 8 dead, search ends, 18 hurt.

Unverified claims are labelled as claims ("IRAN SAYS", "FBI BLAMES").

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png`: 1024x1024, deterministic (two runs are
byte-identical).

## Verification

Two runs of `main.py` produce byte-identical PNGs
(sha256 `40d74c584020916c3f09c9243936b8b80de83c4d07ed1f91c68761d9418fe8cf`),
17,808 bytes (limit 1 MiB), 1024x1024 pixels. Verified in this build
session (Sat 14 Nov 2026 ~03:10 WIB, after the competition opened);
the render was viewed and every label reads correctly.

## License

MIT. See LICENSE.
