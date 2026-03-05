"""
ATS Resume Tailor
-----------------
Paste a job description and get back:
  1. ATS keyword match score
  2. Missing and matched keywords
  3. A fully tailored resume ready to submit
  4. Cover letter talking points
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
import anthropic

load_dotenv()

MASTER_RESUME_PATH = Path(__file__).parent.parent / "data" / "master_resume.txt"
OUTPUT_DIR = Path(__file__).parent / "output"

SYSTEM_PROMPT = """You are an expert ATS optimization specialist and resume strategist.
Your job is to analyze a candidate's master resume against a specific job description
and produce a tailored, ATS-optimized resume that maximizes the candidate's chances
of passing automated screening and impressing human reviewers.

Rules:
- Never invent experience or credentials the candidate does not have
- Mirror language from the job description where truthful
- Keep formatting clean and ATS-safe (no tables, columns, or graphics)
- Be specific and quantified wherever possible
- Prioritize relevance over comprehensiveness"""

TAILOR_PROMPT = """I need you to analyze my master resume against a job description and produce a tailored resume.

Complete all four steps below.

---

STEP 1 — ATS MATCH SCORE
Score my resume against the job description from 0 to 100.
Format:
  Score: XX/100
  Matched keywords: [comma-separated list]
  Missing high-value keywords: [comma-separated list]
  Assessment: [2-3 sentence summary of fit]

---

STEP 2 — TAILORED RESUME
Produce a complete, submission-ready tailored resume using the structure below.
- Choose the best Professional Summary variant and adapt it to this specific role
- Select and reorder the Skills section to lead with the most relevant skills
- Adjust experience bullet emphasis to surface the most relevant work
- Incorporate missing high-value keywords naturally and truthfully
- Use clean single-column formatting

Use this exact structure:
  [Full Name]
  [Contact line]
  [Location line]

  PROFESSIONAL SUMMARY
  [Tailored summary]

  EXPERIENCE
  [Jobs in reverse chronological order with tailored bullets]

  EDUCATION
  [Education]

  CERTIFICATIONS & PROFESSIONAL DEVELOPMENT
  [Certs]

  SKILLS
  [Reordered, role-specific skills]

---

STEP 3 — COVER LETTER TALKING POINTS
List 4-5 specific, concrete things to emphasize in a cover letter or interview
for this role, based on the job description and my background.
Format as bullet points.

---

STEP 4 — RED FLAGS / GAPS
List any genuine gaps between my background and this role's requirements.
Be direct. 2-5 bullet points.

---

MASTER RESUME:
{master_resume}

---

JOB DESCRIPTION:
{job_description}"""


def load_master_resume() -> str:
    if not MASTER_RESUME_PATH.exists():
        print(f"\nERROR: Master resume not found at:\n  {MASTER_RESUME_PATH}")
        print("\nAdd your master resume as data/master_resume.txt")
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


def tailor_resume(job_description: str, master_resume: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nERROR: ANTHROPIC_API_KEY not set.")
        print("Copy .env.example to .env and add your Anthropic API key.")
        print("Get a key at: https://console.anthropic.com")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    prompt = TAILOR_PROMPT.format(
        master_resume=master_resume,
        job_description=job_description
    )

    print("\nAnalyzing job description and tailoring your resume...")
    print("This takes about 20-30 seconds...\n")

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def save_output(content: str, job_description: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"tailored_resume_{timestamp}.txt"

    header = (
        f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n"
        f"{'=' * 70}\n\n"
    )

    output_path.write_text(header + content, encoding="utf-8")
    return output_path


def print_banner():
    print("\n" + "=" * 70)
    print("  ATS RESUME TAILOR — Job Search Toolkit")
    print("=" * 70 + "\n")


def main():
    print_banner()

    # Fail fast — check API key before asking for any input
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set.")
        print("Copy .env.example to .env and add your Anthropic API key.")
        print("Get a key at: https://console.anthropic.com")
        sys.exit(1)

    master_resume = load_master_resume()
    print(f"Master resume loaded. ({len(master_resume.split())} words)\n")

    job_description = get_job_description()
    if not job_description:
        print("No job description provided. Exiting.")
        sys.exit(1)

    result = tailor_resume(job_description, master_resume)

    output_path = save_output(result, job_description)

    print("=" * 70)
    print(result)
    print("\n" + "=" * 70)
    print(f"Saved to: {output_path}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
