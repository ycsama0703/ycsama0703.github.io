Teaser figures for the publication list.

The frame is **4:3** and uses `object-fit: cover`, so it is always filled edge
to edge and anything that is not 4:3 gets cropped by the browser. Hand it a
4:3 image and nothing is lost — `scripts/make_thumb.py` always writes one.

A full paper figure is usually the wrong thing to drop in: at 190px wide a
tall flowchart becomes an unreadable sliver. Crop to the one part that reads
as a thumbnail. The script takes a region and squares it off for you:

    # see the figure with decile rules, to pick a region
    python3 scripts/make_thumb.py ~/Downloads/paper.pdf --page 3 --inspect

    # take the top 45%
    python3 scripts/make_thumb.py ~/Downloads/paper.pdf --page 3 \
        --box 0,0,1,0.45 fingpt

arXiv is a better source than a published PDF: `arxiv.org/e-print/<id>`
is the LaTeX package, with the original figure files inside.

Output is 560x420 (4x the frame, sharp on retina). Keep files under ~200 KB.

Wire a file up in `_data/pub_overrides.yml` (OpenReview-synced papers, keyed by
id) or with `thumb:` on the entry in `_data/publications_manual.yml`.
