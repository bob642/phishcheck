# PhishCheck
An AI-powered phishing email analyzer built with Python, Flask, and the Anthropic Claude API. Paste in a suspicious email and get back a structured risk assessment with specific red flags identified.

## Why I built this

Most enterprise phishing detection (Mimecast, Darktrace, Proofpoint) is expensive, requires admin deployment, and isn't accessible to individuals or small teams. I wanted to see whether a well-prompted LLM could match the analytical reasoning those tools provide — particularly for **behavioral** phishing patterns like business email compromise (BEC), where there are no malicious links or obvious technical indicators to scan for.

The result: a tool that catches scams traditional filters miss.

## What it does

- Accepts an email (sender, subject, body) via a simple web interface
- Sends it to Claude with a structured analyst prompt
- Returns a parsed JSON risk assessment including:
  - Risk level (LOW / MEDIUM / HIGH / CRITICAL) and confidence
  - Specific red flags by category with cited evidence
  - Plain-English explanation
  - Recommended action

## Tech stack

- **Backend:** Python 3.10+, Flask
- **AI:** Anthropic Claude API (Haiku 4.5 — chosen for speed and cost)
- **Frontend:** Plain HTML/CSS/JavaScript (no framework)
- **Config:** python-dotenv for environment-based secrets

## Key engineering decisions

**Constrained output schema.** The system prompt forces Claude to return JSON matching a fixed schema, so the app can process responses programmatically rather than parsing free-form text.

**Defensive parsing.** LLMs occasionally wrap JSON in markdown code fences even when instructed not to. The parser strips fences before deserializing, so the app degrades gracefully when the model misbehaves.

**Precision tuning.** Initial prompts over-flagged legitimate security notifications because asking a model to "look for problems" creates demand characteristics. The final prompt explicitly defines false positives as failures and gives examples of what NOT to flag, balancing recall and precision.

**Model selection.** Haiku 4.5 was chosen over Sonnet or Opus because this task (structured classification against a rubric) doesn't benefit from a larger model. Cheaper, faster, same quality.

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/phishcheck.git
cd phishcheck
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_key_here
```

Get an API key at [console.anthropic.com](https://console.anthropic.com).

## Run

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Example results

PhishCheck correctly identified:
- A typosquatted Amazon phishing email (sender domain `arnaz0n-billing.com`) as CRITICAL
- A real-world Geek Squad/PayPal impersonation scam as CRITICAL
- A business email compromise (BEC) gift card request as HIGH — with no malicious links or urgency keywords present
- A legitimate GitHub SSH notification as LOW / LIKELY_SAFE (no false positive)

## Limitations

- Analysis is only as good as the model. Adversarial prompts inside email content could potentially manipulate output.
- No persistent storage — each analysis is a one-off API call.
- Currently text-only; doesn't analyze headers, attachments, or rendered HTML.

## What's next

- `.eml` file upload (parse raw email format including headers)
- History/logging of analyzed emails
- Inline highlighting of suspicious phrases in the email body
- Option to compare sender domain against known-good domain lists

## Author

Robert Stapleton — IT Service Analyst exploring AI-assisted security workflows.