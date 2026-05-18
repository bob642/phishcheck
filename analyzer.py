"""
PhishCheck - Phishing email analyzer using Claude.
Phase 1: Core analysis engine, terminal output only.
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
client = Anthropic()  # Automatically reads ANTHROPIC_API_KEY from environment


SYSTEM_PROMPT = """You are a cybersecurity analyst specializing in phishing detection. \
Your job is to analyze emails for signs of phishing, social engineering, and other threats.

When given an email, you must evaluate it against these red flag categories:
1. URGENCY_PRESSURE - Language designed to rush the recipient (e.g., "act now", "account suspended")
2. SENDER_MISMATCH - Display name doesn't match sender address, or domain looks spoofed
3. SUSPICIOUS_LINKS - URLs that don't match claimed destinations, shortened URLs, lookalike domains
4. CREDENTIAL_HARVESTING - Requests for passwords, MFA codes, or login via embedded links
5. UNUSUAL_REQUEST - Asks that bypass normal process (gift cards, wire transfers, secrecy)
6. IMPERSONATION - Pretends to be a known brand, executive, or trusted entity
7. STYLE_ANOMALIES - Grammar, spelling, or tone inconsistent with claimed sender

Respond ONLY with valid JSON matching this exact schema. Do not wrap the JSON in markdown code fences (no ```), do not add commentary, return raw JSON only:{
  "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "confidence": "LOW" | "MEDIUM" | "HIGH",
  "red_flags": [
    {
      "category": "URGENCY_PRESSURE" | "SENDER_MISMATCH" | "SUSPICIOUS_LINKS" | "CREDENTIAL_HARVESTING" | "UNUSUAL_REQUEST" | "IMPERSONATION" | "STYLE_ANOMALIES",
      "evidence": "specific quote or observation from the email",
      "severity": "LOW" | "MEDIUM" | "HIGH"
    }
  ],
  "explanation": "Plain-English summary for a non-technical user, 2-3 sentences",
  "recommended_action": "DELETE" | "REPORT_TO_IT" | "VERIFY_WITH_SENDER" | "PROCEED_WITH_CAUTION" | "LIKELY_SAFE"
}

CRITICAL: Only flag genuine indicators, not theoretical risks. A legitimate \
security notification from a real service is not phishing just because phishers \
sometimes imitate that format. If the sender domain, links, and content all \
appear consistent with legitimate communication from the claimed source, return \
an empty red_flags array, risk_level LOW, and recommended_action LIKELY_SAFE.

Specifically, do NOT flag:
- Legitimate URLs to the real domain of the claimed sender
- Informational notifications that don't request action
- Standard automated messages from known services
- Generic phrasing that happens to also appear in phishing

Each red flag must point to a SPECIFIC suspicious element actually present in \
the email — not a hypothetical risk because the email type can be imitated."""


def analyze_email(sender: str, subject: str, body: str) -> dict:
    """Send an email to Claude for phishing analysis and return parsed JSON."""

    email_content = f"""Sender: {sender}
Subject: {subject}

Body:
{body}"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # Cheap and fast - good for this task
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": email_content}
        ]
    )

# Extract the text content from Claude's response
    raw_text = response.content[0].text.strip()

    # Defensive: strip markdown code fences if the model added them anyway.
    # LLMs sometimes wrap JSON in ```json ... ``` even when told not to,
    # so we handle it gracefully instead of crashing.
    if raw_text.startswith("```"):
        # Remove opening fence (```json or just ```)
        raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text
        # Remove closing fence
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse Claude's response as JSON: {e}")
        print(f"Raw response was:\n{raw_text}")
        raise


def print_analysis(analysis: dict) -> None:
    """Pretty-print the analysis result to the terminal."""
    print("\n" + "=" * 60)
    print(f"RISK LEVEL: {analysis['risk_level']}  (confidence: {analysis['confidence']})")
    print(f"RECOMMENDED ACTION: {analysis['recommended_action']}")
    print("=" * 60)

    print(f"\nExplanation:\n  {analysis['explanation']}")

    if analysis['red_flags']:
        print(f"\nRed flags detected ({len(analysis['red_flags'])}):")
        for flag in analysis['red_flags']:
            print(f"  [{flag['severity']}] {flag['category']}")
            print(f"      Evidence: {flag['evidence']}")
    else:
        print("\nNo red flags detected.")
    print()


# Test with a sample phishing email
if __name__ == "__main__":
    test_sender = "robert.s@finance.com"
    test_subject = "Quick favor - need this done before my meeting"
    test_body = """Hi,

I'm heading into a partner meeting and need you to handle something quickly. \
Can you purchase 5 Apple gift cards ($200 each) for client appreciation gifts? \
I'll reimburse you this afternoon. Just send me the codes when you have them.

Don't loop anyone else in on this - I want it to be a surprise for the team.

Thanks,
Robert (sent from mobile)"""

    print("Analyzing test email...")
    result = analyze_email(test_sender, test_subject, test_body)
    print_analysis(result)