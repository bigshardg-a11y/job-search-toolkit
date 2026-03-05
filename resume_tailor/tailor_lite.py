"""
ATS Resume Tailor — Lite Version (No API Credits Required)
-----------------------------------------------------------
Does everything that doesn't need AI:
  1. Keyword match score (0-100)
  2. Matched keywords found in your resume
  3. Missing high-value keywords to add manually
  4. Recommended summary variant (A, B, or C)
  5. Prints the right variant so you know what to copy

What the full version (tailor.py) adds on top of this:
  - Rewrites and tailors your resume automatically
  - Generates cover letter talking points
  - Writes a gap analysis
  - Saves a ready-to-submit document

Run the full version once you have Anthropic API credits:
  python resume_tailor/tailor.py
"""

import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Stopwords — common words that carry no keyword signal
# ---------------------------------------------------------------------------
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "through", "during",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "need", "dare", "ought", "used", "this", "that", "these",
    "those", "i", "we", "you", "he", "she", "it", "they", "what", "which",
    "who", "whom", "when", "where", "why", "how", "all", "each", "every",
    "both", "few", "more", "most", "other", "some", "such", "no", "not",
    "only", "same", "so", "than", "too", "very", "just", "as", "if", "our",
    "your", "their", "its", "my", "his", "her", "us", "them", "also", "well",
    "work", "working", "strong", "including", "ability", "skills", "role",
    "position", "team", "company", "job", "new", "years", "year", "must",
    "will", "within", "across", "while", "ensure", "provide", "support",
    "s", "re", "ve", "ll", "d", "t"
}

# ---------------------------------------------------------------------------
# Keywords that signal which resume variant to use
# ---------------------------------------------------------------------------
BI_ANALYTICS_SIGNALS = {
    "analytics", "data", "reporting", "bi", "business intelligence",
    "dashboard", "sql", "visualization", "people analytics", "workforce",
    "dataset", "metrics", "insights", "tableau", "looker", "power bi",
    "google analytics", "data analyst", "data science", "etl", "pipeline"
}

SECURITY_SIGNALS = {
    "security", "cybersecurity", "infosec", "soc", "siem", "vulnerability",
    "compliance", "grc", "risk", "incident", "threat", "isc2", "cissp",
    "security+", "firewall", "encryption", "audit", "penetration", "pentest"
}

SUPPORT_SIGNALS = {
    "support", "tier", "escalation", "sla", "helpdesk", "troubleshoot",
    "customer success", "account manager", "tam", "technical account",
    "resolution", "ticket", "servicenow", "zendesk", "salesforce", "jira"
}

MASTER_RESUME_PATH = Path(__file__).parent.parent / "data" / "master_resume.txt"
OUTPUT_DIR = Path(__file__).parent / "output"


def extract_keywords(text: str, min_length: int = 3) -> Counter:
    """Extract meaningful words from text, filtered of stopwords."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = text.split()
    return Counter(
        w for w in words
        if len(w) >= min_length and w not in STOPWORDS
    )


def extract_phrases(text: str) -> set:
    """Extract common 2-word technical phrases."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = text.split()
    phrases = set()
    for i in range(len(words) - 1):
        phrase = f"{words[i]} {words[i+1]}"
        if words[i] not in STOPWORDS and words[i+1] not in STOPWORDS:
            phrases.add(phrase)
    return phrases


def calculate_score(jd_keywords: Counter, resume_keywords: Counter) -> tuple:
    """Return (score, matched_list, missing_list)."""
    # Focus on words that appear 2+ times in the JD — those are the ones
    # that really matter to the employer
    important_jd_words = {w for w, c in jd_keywords.items() if c >= 2}

    # Also include all JD words but weight them lower
    all_jd_words = set(jd_keywords.keys())
    resume_words = set(resume_keywords.keys())

    matched_important = important_jd_words & resume_words
    matched_all = all_jd_words & resume_words
    missing = important_jd_words - resume_words

    # Score: 70% weight on important keyword matches, 30% on general overlap
    if important_jd_words:
        important_score = len(matched_important) / len(important_jd_words) * 70
    else:
        important_score = 70

    if all_jd_words:
        general_score = len(matched_all) / len(all_jd_words) * 30
    else:
        general_score = 30

    score = round(important_score + general_score)
    score = min(score, 100)

    # Sort missing by frequency in JD (most frequent = most important)
    missing_sorted = sorted(missing, key=lambda w: jd_keywords[w], reverse=True)

    # Sort matched by frequency in JD
    matched_sorted = sorted(
        matched_important,
        key=lambda w: jd_keywords[w],
        reverse=True
    )

    return score, matched_sorted, missing_sorted


def recommend_variant(jd_text: str) -> tuple:
    """Return (variant_letter, variant_name, reasoning)."""
    text = jd_text.lower()

    bi_score = sum(1 for signal in BI_ANALYTICS_SIGNALS if signal in text)
    sec_score = sum(1 for signal in SECURITY_SIGNALS if signal in text)
    sup_score = sum(1 for signal in SUPPORT_SIGNALS if signal in text)

    if bi_score >= sec_score and bi_score >= sup_score:
        return (
            "B",
            "Business Intelligence / Data Analytics",
            f"JD contains {bi_score} BI/analytics signals "
            f"(vs {sec_score} security, {sup_score} support)"
        )
    elif sec_score > sup_score:
        return (
            "C",
            "Cybersecurity",
            f"JD contains {sec_score} security signals "
            f"(vs {bi_score} BI/analytics, {sup_score} support)"
        )
    else:
        return (
            "A",
            "Senior Technical Support / Tier 3",
            f"JD contains {sup_score} support signals "
            f"(vs {bi_score} BI/analytics, {sec_score} security)"
        )


def get_variant_summary(variant: str, resume_text: str) -> str:
    """Pull the matching variant text from the master resume."""
    markers = {
        "A": "VARIANT A",
        "B": "VARIANT B",
        "C": "VARIANT C"
    }
    next_markers = {
        "A": "VARIANT B",
        "B": "VARIANT C",
        "C": "EXPERIENCE"
    }

    start_marker = markers[variant]
    end_marker = next_markers[variant]

    lines = resume_text.split("\n")
    capturing = False
    result = []

    for line in lines:
        if start_marker in line:
            capturing = True
            continue
        if capturing and end_marker in line:
            break
        if capturing:
            result.append(line)

    return "\n".join(result).strip()


def get_variant_skills(variant: str, resume_text: str) -> str:
    """Pull the matching skills ordering from the master resume."""
    variant_map = {
        "A": "TECHNICAL SUPPORT-FIRST",
        "B": "BI / ANALYTICS-FIRST",
        "C": "CYBERSECURITY-FIRST"
    }
    next_map = {
        "A": "BI / ANALYTICS-FIRST",  # wraps — just take first block
        "B": "CYBERSECURITY-FIRST",
        "C": "TECHNICAL SUPPORT-FIRST"
    }

    start = variant_map[variant]
    end = next_map[variant]

    lines = resume_text.split("\n")
    capturing = False
    result = []

    for line in lines:
        if start in line:
            capturing = True
            continue
        if capturing and end in line:
            break
        if capturing:
            result.append(line)

    return "\n".join(result).strip()


def load_master_resume() -> str:
    if not MASTER_RESUME_PATH.exists():
        print(f"\nERROR: Master resume not found at:\n  {MASTER_RESUME_PATH}")
        sys.exit(1)
    return MASTER_RESUME_PATH.read_text(encoding="utf-8")


def get_job_description() -> str:
    print("Paste the job description below.")
    print("When finished, press Enter on a new line, type END, and press Enter:\n")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def save_output(content: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"lite_analysis_{timestamp}.txt"
    path.write_text(content, encoding="utf-8")
    return path


def build_output(score, matched, missing, variant, variant_name, reasoning,
                 summary_text, skills_text) -> str:
    sep = "=" * 70
    lines = [
        sep,
        "  ATS RESUME TAILOR — LITE ANALYSIS",
        sep,
        "",
        "STEP 1 — ATS MATCH SCORE",
        "-" * 40,
        f"Score: {score}/100",
        "",
        f"Matched keywords ({len(matched)}):",
        "  " + ", ".join(matched[:20]) if matched else "  (none found)",
        "",
        f"Missing high-value keywords ({len(missing)}):",
        "  " + ", ".join(missing[:20]) if missing else "  (none — great fit!)",
        "",
        "ACTION: Before submitting, naturally work these missing keywords",
        "into your resume where truthful and relevant.",
        "",
        sep,
        "",
        "STEP 2 — RECOMMENDED VARIANT",
        "-" * 40,
        f"Use: VARIANT {variant} — {variant_name}",
        f"Why: {reasoning}",
        "",
        "--- COPY THIS SUMMARY ---",
        "",
        summary_text,
        "",
        "--- COPY THIS SKILLS SECTION ---",
        "",
        skills_text,
        "",
        sep,
        "",
        "STEP 3 — WHAT TO DO NEXT",
        "-" * 40,
        "1. Copy the summary and skills section above into your resume",
        "2. Add the missing keywords naturally where they apply",
        "3. For a fully AI-tailored resume with talking points and gap",
        "   analysis, run: python resume_tailor/tailor.py",
        "   (requires Anthropic API credits — ~$0.05 per run)",
        "",
        sep,
    ]
    return "\n".join(lines)


def main():
    print("\n" + "=" * 70)
    print("  ATS RESUME TAILOR — LITE (No API Credits Required)")
    print("=" * 70 + "\n")

    master_resume = load_master_resume()
    print(f"Master resume loaded ({len(master_resume.split())} words)\n")

    job_description = get_job_description()
    if not job_description:
        print("No job description provided. Exiting.")
        sys.exit(1)

    print("\nAnalyzing keywords...")

    jd_keywords = extract_keywords(job_description)
    resume_keywords = extract_keywords(master_resume)

    score, matched, missing = calculate_score(jd_keywords, resume_keywords)
    variant, variant_name, reasoning = recommend_variant(job_description)
    summary_text = get_variant_summary(variant, master_resume)
    skills_text = get_variant_skills(variant, master_resume)

    output = build_output(
        score, matched, missing,
        variant, variant_name, reasoning,
        summary_text, skills_text
    )

    output_path = save_output(output)

    print(output)
    print(f"\nSaved to: {output_path}\n")


if __name__ == "__main__":
    main()
