"""Sentiment classifications for reviews imported from saved Glassdoor pages.

Keyed by Glassdoor review ID (RVW number). Each entry is assigned by reading the
review's full written text (title, pros, cons, advice), never its star rating.
Imported reviews without an entry here are listed as "Not yet classified" and
excluded from all metrics until classified.

    rvw: (score -1..+1, [positive themes], [negative themes], rationale)
"""

CLASSIFICATIONS = {
    105713599: (0.9, ["Compensation", "Work-life balance", "Career growth", "Overall satisfaction"], [],
                "Strong praise for clients, projects, flexibility and pay; states no significant cons."),
    105693470: (0.45, ["Work-life balance", "Remote work", "Learning opportunities", "Coworker relationships"],
                ["Job security", "Career growth"],
                "Positive on flexibility, training and community; cons are inconsistent workload and scarce "
                "high-paying specialist roles. Net positive."),
    105637613: (0.0, ["Compensation"], ["Job security", "Communication"],
                "Title and body balance good wages against no job security and lacking feedback. Mixed "
                "despite a 3-star rating sitting mid-scale."),
    105636131: (-0.05, ["Work-life balance", "Compensation"], ["Culture"],
                "Good work-life balance and pay against a 'rude, stressful, not so welcome' environment. "
                "Written text is mixed although the rating is 4 stars."),
    105621060: (0.6, ["Overall satisfaction", "Work-life balance", "Compensation"],
                ["Organization & process", "Job security"],
                "Interesting projects, flexibility and competitive pay; minor cons on instructions and "
                "availability."),
}
