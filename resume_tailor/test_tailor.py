"""
Test script for ATS Resume Tailor.
Uses a sample job description so you can verify the tool works
without needing to find a real posting first.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from resume_tailor.tailor import load_master_resume, tailor_resume, save_output

SAMPLE_JD = """
Job Title: Senior People Analytics Support Specialist
Company: Apex Workforce Solutions
Location: Remote (US)
Salary: $105,000 - $130,000

About the Role:
We are looking for a Senior People Analytics Support Specialist to join our
Business Intelligence team. You will serve as the primary Tier 3 escalation
point for customers using our workforce analytics and reporting platform,
helping enterprise HR and payroll teams get maximum value from their data.

Responsibilities:
- Serve as the senior escalation point for complex reporting and analytics
  issues within our People Analytics platform
- Diagnose and resolve data population errors, calculation discrepancies,
  and report logic failures for enterprise customers
- Guide customers through advanced report building including joins, filters,
  calculated fields, and data item configuration
- Collaborate cross-functionally with engineering, product, and customer
  success teams to resolve platform-level issues
- Contribute to and maintain internal knowledge base documentation
- Mentor junior support team members and assist with onboarding
- Identify patterns in customer issues and surface product improvement
  opportunities to the product team

Requirements:
- 5+ years of experience in technical support, business intelligence support,
  or a related customer-facing technical role
- Hands-on experience with HR/workforce management platforms and reporting tools
- Strong understanding of SQL or SQL-based query languages
- Experience troubleshooting data issues in BI or analytics environments
- Excellent customer communication skills with ability to explain technical
  concepts to non-technical users
- Proven track record of working effectively in a fully remote environment
- Experience with knowledge base management and documentation

Nice to Have:
- Experience with UKG, Workday, Ceridian, or similar HCM platforms
- Background in People Analytics or HR data
- Cybersecurity awareness or certifications
- Experience mentoring or training team members
- Familiarity with data analysis tools (Google Data Analytics, Python, etc.)

Benefits:
- 100% remote, flexible hours
- $105,000 - $130,000 base salary
- Health, dental, vision
- 401(k) with 4% match
- $2,000 annual learning stipend
- Home office stipend
"""


def main():
    print("\n" + "=" * 70)
    print("  ATS RESUME TAILOR — TEST RUN")
    print("  Using sample job description (People Analytics Support Specialist)")
    print("=" * 70 + "\n")

    # Check for API key first
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set.")
        print("\nTo fix this:")
        print("  1. Go to https://console.anthropic.com")
        print("  2. Create an account and generate an API key")
        print("  3. Create a .env file in the project root:")
        print("       ANTHROPIC_API_KEY=sk-ant-your-key-here")
        print("\nThen run this script again.")
        sys.exit(1)

    print("API key found. Loading master resume...")
    master_resume = load_master_resume()
    print(f"Master resume loaded ({len(master_resume.split())} words)\n")

    print("Sample job description: Senior People Analytics Support Specialist")
    print("Salary range: $105,000 - $130,000 | Remote\n")

    result = tailor_resume(SAMPLE_JD, master_resume)
    output_path = save_output(result, SAMPLE_JD)

    print("=" * 70)
    print(result)
    print("\n" + "=" * 70)
    print(f"Saved to: {output_path}")
    print("=" * 70 + "\n")
    print("Test complete. The tool is working correctly.")
    print("To use with a real job: python resume_tailor/tailor.py")


if __name__ == "__main__":
    main()
