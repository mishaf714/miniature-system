"""Review-level dataset for the Mercor sentiment dashboard.

Every record below was observed in web-search index results on 2026-09-24.
Direct page access to Glassdoor, Indeed, Blind, Reddit, Trustpilot and
Comparably was blocked from the collection environment, so:

  * `headline` is the reviewer-written review title exactly as the search
    index returned it for that URL (verbatim).
  * `excerpt` is a search-index summary of the review body. It is a paraphrase,
    not a verbatim quote, and is only recorded when it was specific to that URL.
  * Missing values are None and are displayed as "Unavailable". Nothing is
    estimated or filled in.

Classification is done by reading the verified written text (headline, plus
excerpt when attribution is "specific"). Star ratings are recorded separately
and never used to classify.
"""

GD = "https://www.glassdoor.com/Reviews/Employee-Review-Mercor-E9031572-RVW{}.htm"

def gd(rvw, headline, score, pos, neg, rationale, *, reviewer=None, date=None,
       date_basis=None, rating=None, excerpt=None, attribution="none", url=None,
       note=None):
    return dict(
        id=f"GD-{rvw}", source="Glassdoor", data_type="Individual review",
        url=url or GD.format(rvw), seq=rvw, headline=headline, excerpt=excerpt,
        excerpt_attribution=attribution, date=date, date_basis=date_basis,
        reviewer_type=reviewer, platform_rating=rating, score=score,
        pos_themes=pos, neg_themes=neg, rationale=rationale, note=note)

def ind(slug, rid, title, headline, score, pos, neg, rationale, *, date=None,
        excerpt=None, attribution="none"):
    return dict(
        id=f"IN-{rid[:8]}", source="Indeed", data_type="Individual review",
        url=f"https://www.indeed.com/cmp/Mercor/reviews/{slug}?id={rid}", seq=None,
        headline=headline, excerpt=excerpt, excerpt_attribution=attribution,
        date=date, date_basis="Search-index summary" if date else None,
        reviewer_type=title, platform_rating=None, score=score, pos_themes=pos,
        neg_themes=neg, rationale=rationale, note=None)

def blind(slug, headline, score, pos, neg, rationale, *, reviewer, date=None,
          excerpt=None, attribution="none", note=None):
    return dict(
        id=f"BL-{slug.rsplit('-',1)[-1]}", source="Blind", data_type="Discussion thread",
        url=f"https://www.teamblind.com/post/{slug}", seq=None, headline=headline,
        excerpt=excerpt, excerpt_attribution=attribution, date=date,
        date_basis="Search-index summary" if date else None, reviewer_type=reviewer,
        platform_rating=None, score=score, pos_themes=pos, neg_themes=neg,
        rationale=rationale, note=note)

# score: None = insufficient written content (listed, excluded from metrics)
REVIEWS = [
    # ---------------- Glassdoor ----------------
    gd(79167149, "Work on cutting-edge technology.", 0.6, ["Learning opportunities"], [],
       "Headline praises the work itself."),
    gd(85001657, "Ideal for Remote Jobs", 0.6, ["Remote work"], [], "Positive about remote work."),
    gd(85002014, "A legitimate company", 0.5, ["Trust & legitimacy", "Overall satisfaction"], [],
       "Affirms legitimacy; mildly positive."),
    gd(85017264, "Great place to work", 0.8, ["Overall satisfaction"], [],
       "Unqualified praise."),
    gd(85074601, "About Mercor", None, [], [],
       "Headline carries no evaluative content; no attributable body text."),
    gd(85312023, "Great Company, Great People!", 0.9, ["Coworker relationships", "Overall satisfaction"], [],
       "Strong praise of company and people."),
    gd(85315989, "Amazing work culture", 0.9, ["Culture"], [],
       "Strong praise of culture."),
    gd(85320274, "Great company, and you get to work on the latest technology", 0.8,
       ["Learning opportunities", "Overall satisfaction"], [],
       "Praise of company and technical exposure."),
    gd(87967235, "Worst software ever", -0.8, [], ["Tools & platform"],
       "Strongly negative about the platform software.", reviewer="Time Pass (job title as listed)"),
    gd(89697245, "They dont pay and are scaming people", -1.0, [], ["Compensation", "Trust & legitimacy"],
       "Alleges non-payment and scam; excerpt consistent.",
       reviewer="AI Prompt Engineer (current, <1 yr)", date="2024-08-01",
       date_basis="Search-index summary",
       excerpt="Pros: \"They are scam and wasting people's time\". Cons: \"NO cons just wasting time\".",
       attribution="specific"),
    gd(92147192, "-", None, [], [], "Headline is a placeholder dash; no attributable body text."),
    gd(92685596, "Poor communication and onboarding process", -0.7, [], ["Communication", "Organization & process"],
       "Complains about communication and onboarding."),
    gd(93715362, "Intelligence Engineer Review", None, [], [],
       "Headline is a job title only.", url="https://www.glassdoor.com.au/Reviews/Employee-Review-Mercor-E9031572-RVW93715362.htm",
       reviewer="Intelligence Engineer"),
    gd(94464014, "Review", None, [], [], "Headline carries no evaluative content."),
    gd(94553647, "There's no company as amazing as Mercor!", 1.0, ["Overall satisfaction"], [],
       "Superlative praise."),
    gd(95294235, "Great company", 0.9, ["Compensation", "Coworker relationships", "Overall satisfaction"], [],
       "Headline is plainly positive. Two searches returned conflicting body summaries for this review "
       "(one strongly positive with a 5-star rating, one 'above average' citing poor communication and "
       "disorganization), so neither body nor rating is used.",
       reviewer="Finance Expert", attribution="conflicting",
       note="Conflicting body summaries across searches; classified from headline only, rating left blank."),
    gd(95878450, "Nice Work Environment", 0.6, ["Culture"], [], "Positive about environment."),
    gd(95912929, "Scam", -0.9, [], ["Trust & legitimacy"],
       "Headline alleges a scam. A positive body excerpt was returned for this URL, but the identical "
       "excerpt was also returned for RVW102492938, so it is not attributable and was not used.",
       attribution="conflicting",
       note="Search summary attached a positive 'AI Evaluator' body to this review and to another; treated as unverified."),
    gd(96104121, "Communication is Nonexistent", -0.8, [], ["Communication"], "Strongly negative on communication."),
    gd(96745147, "Flexible remote work", 0.6, ["Remote work", "Work-life balance"], [],
       "Praises flexibility and remote setup."),
    gd(97203983, "Good Experience", 0.6, ["Overall satisfaction"], [], "Positive overall."),
    gd(97336597, "Good Contract Experience", 0.45,
       ["Compensation", "Work-life balance", "Management"], ["Job security", "Communication"],
       "Positive headline; excerpt praises pay, flexibility and a responsive team but notes sporadic work "
       "and inconsistent communication. Net positive.",
       rating=4,
       excerpt="Good pay and hours, very flexible; responsive team quick to answer questions. Cons: sporadic "
               "opportunities and occasional lack of consistent communication and feedback.",
       attribution="specific"),
    gd(97365185, "Good Attitude and Good Pay", 0.7, ["Compensation", "Culture"], [], "Praises pay and attitude."),
    gd(97627391, "Great Work Experience", 0.8, ["Overall satisfaction"], [], "Strong praise.",
       url="https://www.glassdoor.sg/Reviews/Employee-Review-Mercor-E9031572-RVW97627391.htm"),
    gd(97802740, "not bad but not good", 0.0, [], [], "Explicitly neutral."),
    gd(98048107, "Disorganized and constantly changing", -0.7, [], ["Organization & process", "Communication"],
       "Negative on organization; excerpt specific.",
       excerpt="Instructions (many dictated by the AI lab client) are poorly defined and change daily; changes "
               "communicated only in a very busy Slack channel.",
       attribution="specific"),
    gd(98945044, "got a contract but then they paused it after a few days", -0.6, [], ["Job security"],
       "Negative experience of a paused contract."),
    gd(99352676, "Seems fine so far", 0.25, [], [], "Lukewarm, tentative approval; below positive threshold."),
    gd(99399889, "IF IT SOUNDS TOO GOOD TO BE TRUE…", -0.7, [], ["Trust & legitimacy"],
       "Warning-style headline implying the offer is not as presented.",
       url="https://www.glassdoor.co.uk/Reviews/Employee-Review-Mercor-E9031572-RVW99399889.htm"),
    gd(99536479, "Poor comms, delayed timelines, very amateurish", -0.9, [],
       ["Communication", "Organization & process", "Compensation", "Leadership"],
       "Strongly negative; excerpt specific.",
       excerpt="\"Chaotic - Poorly run - Poor comms.\" Work trial quoted at 6 hours took 10-12 with no extra "
               "pay; Slack questions unanswered; submissions stuck in review 16+ hours; describes leadership as "
               "\"a bunch of 21 year olds trying to play grown ups\".",
       attribution="specific"),
    gd(99925928, "realtively good", 0.4, ["Overall satisfaction"], [], "Qualified but positive."),
    gd(99977356, "Work is fine, when it is there", 0.0, ["Overall satisfaction"], ["Job security"],
       "Balances acceptable work against unreliable availability.",
       url="https://www.glassdoor.co.uk/Reviews/Employee-Review-Mercor-E9031572-RVW99977356.htm"),
    gd(100282453, "Poor communication, unethical requests", -0.85, [], ["Communication", "Leadership"],
       "Strongly negative; alleges unethical requests."),
    gd(100329014, "Good company so far", 0.5, ["Overall satisfaction"], [], "Positive, tentative."),
    gd(100657420, "I LOVE working for Mercor!", 0.95, ["Learning opportunities", "Management", "Culture"], [],
       "Strongly positive; excerpt specific.",
       excerpt="Learned more in three weeks than in two years at a previous job; pace fast, dynamic and fun; "
               "project and team leads patient, helpful and kind.",
       attribution="specific"),
    gd(100795889, "Stay away if you can", -0.95, [],
       ["Management", "Job security", "Workload", "Compensation", "Communication"],
       "Strongly negative; excerpt specific.", date="2025-11-13", date_basis="Search-index summary",
       excerpt="Management threatens new workers with termination; cycle of hiring and firing; heavy workload "
               "without fair pay; payment withheld after a vague \"policy violation\" with no appeal; minimal "
               "support communication.",
       attribution="specific"),
    gd(100821156, "Good experience", 0.6, ["Overall satisfaction"], [], "Positive overall."),
    gd(101257023, "Started ok, ultimately the company will offer you lower and lower contracts until you stop working.",
       -0.7, [], ["Compensation", "Job security", "Organization & process"],
       "Negative overall despite an 'ok' start; excerpt specific.",
       excerpt="Offered 7 projects, 5 never started (unpaid onboarding or vanished); after 4 months with an "
               "excellent QA score the project was cancelled and replaced by a much lower-paying copy.",
       attribution="specific",
       note="A search summary gave 2025-11-13, the same date as RVW100795889; treated as unverified and left blank."),
    gd(101269595, "Good company", 0.6, ["Overall satisfaction"], [], "Positive overall."),
    gd(102136443, "What a great and easy way to make some money", 0.8, ["Compensation", "Overall satisfaction"], [],
       "Strongly positive about earning opportunity.",
       reviewer="AI Model Trainer (per search summary, unverified)"),
    gd(102421292, "So many red flags", -0.8, [], ["Overall satisfaction"],
       "Strongly negative warning.", reviewer="Operations"),
    gd(102492938, "Terrible work culture", -0.85, [], ["Culture"],
       "Headline strongly negative. The body excerpt returned was the same positive text returned for "
       "RVW95912929, so it was not used.",
       attribution="conflicting"),
    gd(103274438, "Great", 0.7, ["Overall satisfaction"], [], "Positive, brief."),

    # ---------------- Indeed ----------------
    ind("good-pay", "b61012dc1a6cfb7b", None, "good pay", 0.6,
        ["Compensation", "Work-life balance", "Remote work"], [],
        "Positive headline; excerpt praises rates, flexibility and remote work.", date="2025-08-08",
        excerpt="Hourly rates for most projects are competitive; tons of flexibility with hours; remote.",
        attribution="specific"),
    ind("overall-a-great-experience", "a28c130e684998f9", "AI Trainer", "Overall a great experience", 0.8,
        ["Overall satisfaction", "Management", "Learning opportunities"], [],
        "Strongly positive; excerpt specific.", date="2025-12-24",
        excerpt="Thought-provoking tasks, clear instructions and expectations, project managers open to feedback.",
        attribution="specific"),
    ind("working-at-mercor-is-likely-to-be-highly-detrimental-to-your-mental-health-due-to-the-serious-technology-issues-wage-theft-and-communication-issues",
        "518b0143e30d119c", "Independent Contractor",
        "Working at Mercor is likely to be highly detrimental to your mental health due to the serious "
        "technology issues, wage theft, and communication issues.", -0.95, [],
        ["Tools & platform", "Compensation", "Communication", "Work-life balance"],
        "Severe complaints about technology, pay and communication."),
    ind("good-opportunities-especially-for-part-time", "c4c639c94809d5f6", "Computer Specialist",
        "Good opportunities, especially for part time.", 0.5, ["Overall satisfaction", "Work-life balance"], [],
        "Positive with a scope qualifier (part time)."),
    ind("good-pay-and-flexible-work", "b4631d35f5579eb0", "AI Trainer", "Good pay and flexible work", 0.65,
        ["Compensation", "Work-life balance"], [], "Positive on pay and flexibility."),
    ind("mercor-is-solid", "4afae4c3cd35828e", "Audio Trainer", "Mercor is solid.", 0.5,
        ["Overall satisfaction"], [], "Positive, measured."),

    # ---------------- Blind (discussion threads) ----------------
    blind("mercor-interview-made-me-miss-my-toxic-job-qxbg1go7", "Mercor interview made me miss my toxic job",
          -0.7, [], ["Culture", "Workload"], "Negative comparison with a 'toxic' previous job.",
          reviewer="Candidate (interview experience)"),
    blind("mercor-996-work-expectation-g0fkaxzk", "Mercor 996 work expectation", -0.3, [],
          ["Workload", "Work-life balance"],
          "Describes a recruiter's 996 expectation (9am-9pm, six days). Mostly factual; implied concern. "
          "Scores inside the mixed/neutral band.",
          reviewer="Candidate (recruiter outreach)",
          excerpt="Recruiter described a 996 culture: SF office Mon-Fri 9-9, plus Saturday remote.",
          attribution="specific"),
    blind("thoughts-on-mercor-3glbw3aa", "Thoughts on Mercor", None, [], [],
          "Headline is a question; no attributable body text.", reviewer="Anonymous Blind user",
          date="2026-07-15"),
    blind("what-does-it-look-like-to-work-at-mercor-as-an-fte-h3j5gitm",
          "What does it look like to work at Mercor as an FTE?", None, [], [],
          "Question, no evaluative content.", reviewer="Anonymous Blind user"),
    blind("just-had-a-interview-with-mercor-btp027n1", "Just had a interview with Mercor - Software Engineer",
          None, [], [], "Descriptive headline, no evaluative content.", reviewer="Candidate"),
]

# Aggregated platform figures (NOT individual reviews). Snapshot dates are not
# shown in the search index, and different snapshots disagree, so ranges are kept.
AGGREGATES = [
    dict(source="Glassdoor", metric="Overall rating", value="4.1–4.2 / 5",
         detail="4.2 from 188 reviews in one indexed snapshot; 4.1 from 722–734 reviews in a later one",
         url="https://www.glassdoor.com/Reviews/Mercor-Reviews-E9031572.htm", rating_mid=4.15),
    dict(source="Glassdoor", metric="Recommend to a friend", value="78–90%",
         detail="Varies across indexed snapshots", url="https://www.glassdoor.com/Reviews/Mercor-Reviews-E9031572.htm"),
    dict(source="Glassdoor", metric="Sub-ratings", value="Comp 4.3 · WLB 4.2–4.4 · Culture 3.8–4.1 · Career 3.9–4.2",
         detail="Varies across indexed snapshots", url="https://www.glassdoor.com/Reviews/Mercor-Reviews-E9031572.htm"),
    dict(source="Glassdoor", metric="Job-title review pages", value="Domain Expert · Senior Domain Expert · Consultant · Generalist Expert",
         detail="Glassdoor has per-title review pages for these contractor roles and says its best reviews come from Domain Expert, "
                "Senior Domain Expert and Independent Contractor. The individual reviews on those pages were not exposed by search",
         url="https://www.glassdoor.com/Reviews/Mercor-Domain-Expert-Reviews-EI_IE9031572.0,6_KO7,20.htm"),
    dict(source="Indeed", metric="Overall rating", value=None,
         detail="Not visible in search results", url="https://www.indeed.com/cmp/Mercor/reviews"),
    dict(source="Blind", metric="Company reviews", value="0 reviews, no rating",
         detail="Blind lists no formal company reviews; only discussion threads",
         url="https://www.teamblind.com/company/Mercor/reviews"),
    dict(source="Trustpilot", metric="Overall rating", value="≈4 / 5",
         detail="mercor.io; review count 226–682 across snapshots. Individual reviews not reachable, so none classified",
         url="https://www.trustpilot.com/review/mercor.io", rating_mid=4.0),
    dict(source="Reddit", metric="Posts", value=None,
         detail="Blocked for both direct access and the search tool; no posts collected", url="https://www.reddit.com/search/?q=mercor"),
    dict(source="Comparably", metric="Company profile", value=None,
         detail="No Mercor profile found (searches returned Mercer/Merck)", url="https://www.comparably.com/"),
]
