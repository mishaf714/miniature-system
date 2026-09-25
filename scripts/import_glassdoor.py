"""Extract reviews from Glassdoor review pages saved in a browser.

Save each Glassdoor review page (Ctrl/Cmd+S, "Webpage, HTML only" or complete)
into data/glassdoor_html/, then run:

    python3 scripts/import_glassdoor.py

Writes data/glassdoor_imported.json with one record per review, fields copied
verbatim from the page. Saved pages contain the viewer's account details, so
the HTML folder is git-ignored; only the extracted review fields are kept.
"""
import json, re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "glassdoor_html"
OUT = ROOT / "data" / "glassdoor_imported.json"


def text(node):
    return node.get_text("\n", strip=True) if node else None


def parse_card(art, page):
    rid = re.search(r"review_id=(\d+)", art.get("data-brandviews", ""))
    link = art.select_one("a[href*=RVW]")
    if not rid and link:
        rid = re.search(r"RVW(\d+)", link["href"])
    if not rid:
        return None
    date_raw = text(art.select_one("[class*=Timestamp_reviewDate]"))
    rating = text(art.select_one("[data-test=review-rating-label]"))
    tag = text(art.select_one("[data-test=content-avatar-tag]"))
    location = None
    if tag and "\n" in tag:
        tag, location = tag.split("\n", 1)
    return dict(
        rvw=int(rid.group(1)),
        url=f"https://www.glassdoor.com/Reviews/Employee-Review-Mercor-E9031572-RVW{rid.group(1)}.htm",
        date=datetime.strptime(date_raw, "%b %d, %Y").date().isoformat() if date_raw else None,
        rating=float(rating) if rating else None,
        title=text(art.select_one("h3")),
        job_title=text(art.select_one("[data-test=content-avatar-label]")),
        employment=tag,
        location=location,
        pros=text(art.select_one("[data-test=review-text-PROS]")),
        cons=text(art.select_one("[data-test=review-text-CONS]")),
        advice=text(art.select_one("[data-test=review-text-ADVICE]")),
        truncated=bool(art.find(string=re.compile(r"^\s*Show more\s*$"))),
        saved_page=page,
    )


def main():
    existing = {r["rvw"]: r for r in json.loads(OUT.read_text())} if OUT.exists() else {}
    found = 0
    for f in sorted(SRC.glob("*.htm*")):
        soup = BeautifulSoup(f.read_text(encoding="utf-8", errors="replace"), "html.parser")
        for art in soup.select("article[data-test=review-detail]"):
            r = parse_card(art, soup.title.get_text(strip=True) if soup.title else f.name)
            if not r:
                continue
            found += 1
            old = existing.get(r["rvw"])
            # Keep the most complete copy (an expanded review beats a truncated one).
            if not old or (old["truncated"] and not r["truncated"]):
                existing[r["rvw"]] = r
    rows = sorted(existing.values(), key=lambda r: -r["rvw"])
    OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    print(f"{found} review cards read, {len(rows)} unique reviews in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
