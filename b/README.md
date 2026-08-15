# /b/ — permanent bookmark QR redirects

    /b/<T>/<B>/<L>        T = title    t01, t02, ...
                          B = bookmark t01's designs are b1..b4, numbered per title
                          L = location l00 = no fixed location, l01+ = venue in the register

Printed example: `https://prahran.press/b/t01/b1/l04`

That address is permanent — it is photographed into every QR code and can never change.
Where it *lands* is controlled entirely by `b/bookmarks.json`.

## Change where a batch lands

1. Edit `b/bookmarks.json` — set `"to"` for that batch.
2. `python3 tools/build-bookmarks.py`
3. `git add b && git commit -m "Point t01/b3/l04 at Hares & Hyenas" && git push`

`"to": null` means "use this title's default page". Set it back to `null` to bring a
batch home when a shop stops stocking the book.

## Add a location

Add it to `locations`, then add `"b3/l04": { "to": null }` to that title's `batches`.
Re-run the script. New URL, new QR to generate — existing bookmarks unaffected.

## Add a title

New `t03` block with its own default page and its own `b1`, `b2`… numbering.
Design numbers are per-title, so they never collide across books.

## Tracking

Internal destinations carry `?ref=<design>&loc=<location>`, which GA4 (G-M64RTG88Y3)
records. Read it under Reports → Engagement → Pages and screens with the
"Page path + query string" dimension: each design-and-location pair is its own row.

External destinations get UTM tags instead. Those land in the bookshop's analytics,
not ours — once a batch points at a shop, we go blind on it. That is inherent, not a bug.

## Why the URLs are as short as they are

QR version 4 at error-correction H holds 34 characters. `/b/t01/b1/l04` is exactly 34.
Spelling the design `bm1` instead of `b1` pushes it to 35, which forces version 5 —
37 modules instead of 33, i.e. a denser code in the same printed area, with less
tolerance for the logo punched through the middle. Hence `b1`, not `bm1`.

Register of what was printed and where it went:
`Prahran Publishing/Bookmarks/bookmark-register.csv`
