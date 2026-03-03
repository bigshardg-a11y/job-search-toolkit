# ATS Resume Tailor

Paste any job description and get back a tailored, ATS-optimized resume in
about 30 seconds.

## What It Does

1. **ATS Match Score** — Scores your resume against the JD (0-100), lists
   matched and missing keywords, and gives a fit assessment
2. **Tailored Resume** — Selects the right summary variant, reorders skills
   to lead with what the role cares about, and mirrors JD language throughout
3. **Cover Letter Talking Points** — 4-5 specific things to hit in your
   cover letter or first interview
4. **Gap Analysis** — Honest list of where your background falls short for
   this specific role

Output is printed to the terminal and saved to `resume_tailor/output/`.

## Setup

1. Make sure you're in the project root
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
   Get a key at: https://console.anthropic.com

## Usage

```bash
python resume_tailor/tailor.py
```

Paste the job description when prompted. Type `END` on its own line when done.

## Output

Saved to: `resume_tailor/output/tailored_resume_YYYYMMDD_HHMMSS.txt`

Each run creates a new timestamped file so you never overwrite a previous result.
