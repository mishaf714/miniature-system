"""Compute sentiment metrics from data/reviews_raw.py and build the dashboard.

Outputs:
  data/reviews.csv      review-level dataset (every record, incl. excluded ones)
  data/metrics.json     all calculated metrics
  dashboard/index.html  self-contained dashboard (data embedded)

Run:  python3 scripts/build.py
"""
import csv, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data"))
from reviews_raw import REVIEWS, AGGREGATES  # noqa: E402
from classifications import CLASSIFICATIONS  # noqa: E402

IMPORTED = ROOT / "data" / "glassdoor_imported.json"


def imported_reviews():
    """Reviews extracted from saved Glassdoor pages (full verbatim text)."""
    if not IMPORTED.exists():
        return []
    out = []
    for g in json.loads(IMPORTED.read_text()):
        c = CLASSIFICATIONS.get(g["rvw"])
        body = "\n".join(f"{k}: {g[k.lower()]}" for k in ("Pros", "Cons", "Advice") if g.get(k.lower()))
        who = ", ".join(x for x in (g["job_title"], g["employment"], g["location"]) if x)
        out.append(dict(
            id=f"GD-{g['rvw']}", source="Glassdoor", data_type="Individual review", url=g["url"],
            seq=g["rvw"], headline=g["title"], excerpt=body, excerpt_attribution="verbatim",
            date=g["date"], date_basis="Glassdoor saved page", reviewer_type=who or None,
            platform_rating=g["rating"], score=c[0] if c else None,
            pos_themes=c[1] if c else [], neg_themes=c[2] if c else [],
            rationale=c[3] if c else "Imported; not yet classified.", pending=c is None,
            note="Text shown truncated on the saved page (\"Show more\")." if g["truncated"] else None))
    return out

COLLECTED_ON = "2026-09-24"
POS_T, NEG_T = 0.35, -0.35            # sentiment-score thresholds
POINTS = {"Positive": 100, "Mixed/Neutral": 50, "Negative": 0}
SOURCES = ["Glassdoor", "Indeed", "Blind", "Reddit", "Comparably", "Trustpilot"]

# Contractor-role scope: reviews whose reviewer job title contains one of these words.
ROLE_KEYWORDS = ["consultant", "expert", "specialist", "generalist"]
SCOPES = {
    "contractor": dict(label="Consultant / Expert / Specialist / Generalist titles",
                       test=lambda r: any(k in (r["reviewer_type"] or "").lower() for k in ROLE_KEYWORDS)),
    "all": dict(label="All reviewers", test=lambda r: True),
}


def classify(score, pending=False):
    if pending:
        return "Not yet classified"
    if score is None:
        return "Insufficient text"
    if score >= POS_T:
        return "Positive"
    if score <= NEG_T:
        return "Negative"
    return "Mixed/Neutral"


def summarize(rows):
    n = len(rows)
    if n == 0:
        return dict(n=0, positive=0, negative=0, mixed=0, pos_pct=None, neg_pct=None,
                    mixed_pct=None, contentment=None, ci=None, mean_sentiment=None)
    c = Counter(r["classification"] for r in rows)
    pts = [POINTS[r["classification"]] for r in rows]
    mean = sum(pts) / n
    ci = None
    if n > 1:
        sd = math.sqrt(sum((p - mean) ** 2 for p in pts) / (n - 1))
        half = 1.96 * sd / math.sqrt(n)
        ci = [round(max(0, mean - half)), round(min(100, mean + half))]
    return dict(
        n=n, positive=c["Positive"], negative=c["Negative"], mixed=c["Mixed/Neutral"],
        pos_pct=round(100 * c["Positive"] / n, 1), neg_pct=round(100 * c["Negative"] / n, 1),
        mixed_pct=round(100 * c["Mixed/Neutral"] / n, 1), contentment=round(mean, 1), ci=ci,
        mean_sentiment=round(sum(r["score"] for r in rows) / n, 2))


def prepare():
    rows = []
    imported = imported_reviews()
    have = {r["id"] for r in imported}
    for r in [r for r in REVIEWS if r["id"] not in have] + imported:
        r = dict(r)
        r["classification"] = classify(r["score"], r.get("pending", False))
        r["year"] = int(r["date"][:4]) if r.get("date") else None
        r["included"] = r["score"] is not None
        r["text_basis"] = {"verbatim": "Full review text (Glassdoor page)",
                           "specific": "Headline + search excerpt"}.get(r["excerpt_attribution"], "Headline only")
        r["collected_on"] = COLLECTED_ON
        r["role_match"] = SCOPES["contractor"]["test"](r)
        rows.append(r)
    return rows


def compute(rows):
    rows = [dict(r) for r in rows]
    inc = [r for r in rows if r["included"]]
    n_total = len(inc)
    for r in rows:
        r["contentment_points"] = POINTS.get(r["classification"])
        r["contentment_contribution"] = (round(POINTS[r["classification"]] / n_total, 3)
                                         if r["included"] else None)

    by_source = {s: summarize([r for r in inc if r["source"] == s]) for s in SOURCES}
    years = sorted({r["year"] for r in inc if r["year"]})
    by_year = [dict(year=y, **summarize([r for r in inc if r["year"] == y])) for y in years]
    by_year.append(dict(year=None, **summarize([r for r in inc if r["year"] is None])))
    by_source_year = []
    for s in SOURCES:
        for y in years + [None]:
            sub = [r for r in inc if r["source"] == s and r["year"] == y]
            if sub:
                by_source_year.append(dict(source=s, year=y, **summarize(sub)))

    # Year-level counts including excluded records (volume view)
    volume_all = Counter((r["year"], r["included"]) for r in rows)

    # Glassdoor ordered by review ID (sequence, not dates)
    gd = sorted([r for r in inc if r["source"] == "Glassdoor"], key=lambda r: r["seq"])
    half = len(gd) // 2
    gd_seq = None if len(gd) < 6 else dict(
        points=[dict(id=r["id"], seq=r["seq"], classification=r["classification"],
                     score=r["score"], headline=r["headline"], date=r["date"]) for r in gd],
        earlier=dict(range=[gd[0]["seq"], gd[half - 1]["seq"]], **summarize(gd[:half])),
        later=dict(range=[gd[half]["seq"], gd[-1]["seq"]], **summarize(gd[half:])),
        anchors=[dict(seq=r["seq"], date=r["date"]) for r in gd if r["date"]],
    )

    themes = defaultdict(lambda: {"positive": 0, "negative": 0})
    for r in inc:
        for t in r["pos_themes"]:
            themes[t]["positive"] += 1
        for t in r["neg_themes"]:
            themes[t]["negative"] += 1
    theme_list = sorted(({"theme": k, **v} for k, v in themes.items()),
                        key=lambda t: -(t["positive"] + t["negative"]))

    rated = [r for r in inc if r["platform_rating"] is not None]
    metrics = dict(
        collected_on=COLLECTED_ON,
        thresholds=dict(positive=POS_T, negative=NEG_T),
        points=POINTS,
        overall=summarize(inc),
        records_total=len(rows),
        records_excluded=len(rows) - n_total,
        by_source=by_source,
        by_year=by_year,
        by_source_year=by_source_year,
        volume_by_year=[dict(year=y, included=volume_all[(y, True)], excluded=volume_all[(y, False)])
                        for y in sorted({r["year"] for r in rows if r["year"]}) + [None]],
        glassdoor_sequence=gd_seq,
        themes=theme_list,
        individual_ratings=dict(n=len(rated),
                                mean=round(sum(r["platform_rating"] for r in rated) / len(rated), 2)
                                if rated else None),
        aggregates=AGGREGATES,
    )
    return metrics, rows


def main():
    base = prepare()
    scopes = {}
    for key, sc in SCOPES.items():
        metrics, rows = compute([r for r in base if sc["test"](r)])
        metrics["scope_label"] = sc["label"]
        metrics["role_keywords"] = ROLE_KEYWORDS
        scopes[key] = dict(metrics=metrics, reviews=rows)
        o = metrics["overall"]
        print(f"[{key}] classified={o['n']} excluded={metrics['records_excluded']} contentment={o['contentment']} "
              f"pos={o['positive']} neg={o['negative']} mixed={o['mixed']}")
        for s_, v in metrics["by_source"].items():
            if v["n"]:
                print(f"    {s_:11} n={v['n']:2} score={v['contentment']}")

    (ROOT / "data" / "metrics.json").write_text(
        json.dumps({k: v["metrics"] for k, v in scopes.items()}, indent=2, ensure_ascii=False))
    rows = scopes["all"]["reviews"]

    (ROOT / "data" / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))

    cols = ["id", "source", "data_type", "url", "date", "date_basis", "year", "reviewer_type",
            "headline", "excerpt", "excerpt_attribution", "text_basis", "platform_rating",
            "classification", "score", "pos_themes", "neg_themes", "contentment_points",
            "contentment_contribution", "included", "role_match", "rationale", "note", "collected_on"]
    with open(ROOT / "data" / "reviews.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            out = dict(r)
            out["pos_themes"] = "; ".join(r["pos_themes"])
            out["neg_themes"] = "; ".join(r["neg_themes"])
            w.writerow(out)

    template = (ROOT / "dashboard" / "template.html").read_text(encoding="utf-8")
    payload = json.dumps(dict(default="contractor", scopes=scopes), ensure_ascii=False).replace("</", "<\\/")
    (ROOT / "dashboard" / "index.html").write_text(template.replace("/*__DATA__*/null", payload),
                                                   encoding="utf-8")


if __name__ == "__main__":
    main()
