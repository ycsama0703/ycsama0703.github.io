"""
Fetch publications by an OpenReview profile and dump to _data/publications.yml.

Queries both OpenReview API v1 (legacy venues) and v2 (newer venues).
Written for unauthenticated, public-only access — no credentials needed.
"""

import os
import sys
import yaml
import openreview

PROFILE_ID = os.environ.get("OPENREVIEW_PROFILE_ID", "~Yuncong_Liu6")
# Used as the `term` for OpenReview's full-text search (which requires non-empty term).
# Results are filtered down to PROFILE_ID afterwards.
SEARCH_TERM = os.environ.get("OPENREVIEW_SEARCH_TERM", "Yuncong Liu")
OUTPUT = os.environ.get(
    "OPENREVIEW_OUTPUT",
    os.path.join(os.path.dirname(__file__), "..", "_data", "publications.yml"),
)


def _content_get(content, key, default=""):
    """OpenReview v2 wraps fields as {"value": ...}; v1 stores raw values."""
    v = content.get(key, default)
    if isinstance(v, dict) and "value" in v:
        return v["value"]
    return v


def normalize(note, api_version):
    c = note.content or {}
    title = _content_get(c, "title", "").strip()
    authors = _content_get(c, "authors", []) or []
    if isinstance(authors, str):
        authors = [a.strip() for a in authors.split(",")]
    venue = _content_get(c, "venue", "") or _content_get(c, "venueid", "")
    abstract = _content_get(c, "abstract", "") or ""
    pdf = _content_get(c, "pdf", "")
    forum = note.forum or note.id

    # Year: try multiple sources
    year = ""
    venueid = _content_get(c, "venueid", "") or ""
    for token in (venueid + " " + venue).split("/"):
        token = token.strip()
        if token.isdigit() and len(token) == 4:
            year = token
            break
    if not year and getattr(note, "cdate", None):
        # cdate is ms epoch
        from datetime import datetime
        try:
            year = str(datetime.utcfromtimestamp(note.cdate / 1000).year)
        except Exception:
            pass

    pdf_url = ""
    if pdf:
        pdf_url = pdf if pdf.startswith("http") else f"https://openreview.net{pdf}"

    return {
        "title": title,
        "authors": authors,
        "venue": venue,
        "year": year,
        "abstract": abstract,
        "pdf": pdf_url,
        "openreview": f"https://openreview.net/forum?id={forum}",
        "id": note.id,
    }


def fetch_v2(profile_id, term=None):
    client = openreview.api.OpenReviewClient(baseurl="https://api2.openreview.net")
    notes = client.get_all_notes(content={"authorids": profile_id})
    return [normalize(n, 2) for n in notes]


def fetch_v1(profile_id, term=None):
    client = openreview.Client(baseurl="https://api.openreview.net")
    notes = client.get_all_notes(content={"authorids": profile_id})
    return [normalize(n, 1) for n in notes]


def main():
    pubs = []
    seen = set()

    for fetcher, label in ((fetch_v2, "v2"), (fetch_v1, "v1")):
        try:
            for p in fetcher(PROFILE_ID, SEARCH_TERM):
                if p["id"] in seen:
                    continue
                if not p["title"]:
                    continue
                seen.add(p["id"])
                pubs.append(p)
            print(f"[{label}] OK", file=sys.stderr)
        except Exception as e:
            print(f"[{label}] failed: {e}", file=sys.stderr)

    pubs.sort(key=lambda p: (p["year"] or "0"), reverse=True)

    out_path = os.path.abspath(OUTPUT)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            pubs, f, allow_unicode=True, sort_keys=False, default_flow_style=False
        )
    print(f"Wrote {len(pubs)} publications to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
