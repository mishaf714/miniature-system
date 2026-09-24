# Mercor Employee & Contractor Sentiment

A dashboard of how employees, contractors and candidates describe working with Mercor.
Each review is classified from its **written text**, not its star rating.

Open `dashboard/index.html` in a browser. It is self-contained, with the data embedded.

## Layout

| Path | What it is |
|---|---|
| `data/reviews_raw.py` | Source dataset: one record per review with its URL, verbatim headline, excerpt, date, reviewer type, rating, sentiment score, themes and rationale. Also holds the platform-level aggregate figures. |
| `scripts/build.py` | Classifies reviews, computes every metric, writes the outputs below. |
| `data/reviews.csv` | Review-level export (generated). |
| `data/metrics.json` | All calculated metrics (generated). |
| `dashboard/template.html` | Dashboard source; `build.py` injects the data. |
| `dashboard/index.html` | Built dashboard (generated). |

Rebuild after editing the data: `python3 scripts/build.py`

## Reviewer scope

The dashboard opens on **contractor roles**: reviews whose reviewer job title contains
"consultant", "expert" or "specialist" (`ROLE_KEYWORDS` in `scripts/build.py`). A toggle
switches to all reviewers. Only reviews with a visible, matching job title are kept, and
most Glassdoor reviews surfaced without one, so this scope is currently very small.
`data/reviews.csv` has a `role_match` column; `data/metrics.json` holds both scopes.

## Methodology

- **Sentiment score** from −1 to +1, assigned per review from its verified written text.
  Positive ≥ +0.35, Negative ≤ −0.35, otherwise Mixed/Neutral. Records with no
  evaluative text (for example a headline of "Review") are listed but excluded.
- **Contentment score (0–100)** = (100·Positive + 50·Mixed + 0·Negative) ÷ classified reviews
  = Positive% + ½·Mixed%. The same formula is used for every source, year and group.

## Data provenance and limits

Collected 2026-09-24. The collection environment could not open Glassdoor, Indeed, Blind,
Reddit, Trustpilot or Comparably pages directly, so records come from web-search index
results:

- Headlines are verbatim and tied to the review URL. Body excerpts are search-index
  paraphrases, used only when they matched that one review.
- Reddit could not be reached at all, and Comparably has no Mercor profile. Both are marked
  unavailable. Trustpilot has an aggregate rating only.
- Few reviews have a verified date. The dashboard also orders Glassdoor reviews by review
  ID, which Glassdoor assigns in submission order.
- The sample is not random. Glassdoor's own aggregate (4.1–4.2★) is more positive than
  this sample.

Nothing is estimated or generated. Missing values are shown as "Unavailable".
