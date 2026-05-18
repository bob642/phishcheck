"""
PhishCheck - Flask web app wrapping the analyzer.
"""

from flask import Flask, render_template, request, jsonify
from analyzer import analyze_email

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze an email submitted via the form."""
    data = request.get_json()
    sender = data.get("sender", "").strip()
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()

    if not sender or not subject or not body:
        return jsonify({"error": "All three fields are required."}), 400

    try:
        result = analyze_email(sender, subject, body)
        return jsonify(result)
    except Exception as e:
        # Log to console for debugging, return generic error to user
        print(f"Analysis failed: {e}")
        return jsonify({"error": "Analysis failed. Please try again."}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)