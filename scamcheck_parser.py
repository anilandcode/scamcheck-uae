"""
ScamCheck UAE - Day 1 parser (MVP)
Simple, rule-based scoring. No real/fake verdict, only risk + evidence.
Does NOT store passport numbers. Only scores the text.
"""

import re

# 1. MOHRE numbers - a real MOHRE offer must have these
TRANSACTION_RE = re.compile(r"transaction\s*(?:no\.?|number)\s*[:#]?\s*(\d+)", re.I)
COMPANY_RE = re.compile(r"company\s*(?:no\.?|number)\s*[:#]?\s*(\d+)", re.I)

# 2. Fee demand - employer must pay in UAE, not the worker
FEE_RE = re.compile(
    r"(pay|payment|fee).*(visa|processing|agent|joining)"
    r"|western union|pay.*AED|pay to (a )?personal account|usdt|crypto",
    re.I,
)

# 3. Gmail / Yahoo only + no company domain
FREE_EMAIL_RE = re.compile(r"[a-z0-9._%+-]+@(?:gmail|yahoo|hotmail)\.com", re.I)
SALARY_RE = re.compile(r"AED\s*([\d,]+)", re.I)


def score_offer(text: str):
    flags = []
    score = 0

    if not TRANSACTION_RE.search(text) and not COMPANY_RE.search(text):
        score += 40
        flags.append("missing MOHRE transaction / company number (+40)")

    if FEE_RE.search(text):
        score += 40
        flags.append("asks you to pay a fee (+40)")

    if FREE_EMAIL_RE.search(text):
        score += 30
        flags.append("gmail / yahoo only, no company domain (+30)")

    # Simple salary sanity check for a cleaner-type role
    m = SALARY_RE.search(text)
    if m:
        try:
            salary = int(m.group(1).replace(",", ""))
            if salary >= 10000 and "cleaner" in text.lower():
                score += 0  # already covered by the 3 flags above, kept for logging
                flags.append("note: AED 10,000 salary for a cleaner role is unrealistic")
        except ValueError:
            pass

    level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return {"score": score, "level": level, "flags": flags}


# Test cases - example strings only, no real person data
FAKE_EXAMPLE = """
Cleaner - AED 10,000 a month
Pay AED 2500 visa fee via Western Union before joining
Contact: jobs.dubai@gmail.com
"""

REAL_FORMAT_EXAMPLE = """
Transaction Number: 12345678
Company Number: 7654321
Job Title: Cleaner
Salary: AED 3000 per month
"""

if __name__ == "__main__":
    print("FAKE:", score_offer(FAKE_EXAMPLE))
    print("REAL FORMAT:", score_offer(REAL_FORMAT_EXAMPLE))
