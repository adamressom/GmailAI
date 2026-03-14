import os
import json
import base64
import re
from flask import Flask, render_template, request, abort, redirect, url_for, session, flash
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google import genai

# ─── APP CONFIG ──────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-prod")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# ─── KEYS / CONFIG ───────────────────────────────────────────────────────────

GOOGLE_CLIENT_SECRETS_FILE = os.environ.get(
    "GOOGLE_CLIENT_SECRETS_FILE", "client_secrets.json"
)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

GEMINI_API_KEY = "AIzaSyAkQRh6gr4Gs-BWR5jJkJ-L7u1rRVSEbDk"
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    gemini_client = None

# ─── CATEGORY META ───────────────────────────────────────────────────────────

CATEGORY_META = {
    "Career": {
        "icon": "💼",
        "description": "Recruiters, internship process updates, and career-related communication."
    },
    "Resources": {
        "icon": "🧰",
        "description": "Campus help such as CAPS, tutoring, financial support, and student services."
    },
    "Opportunities": {
        "icon": "🚀",
        "description": "Research, internships, leadership programs, and developmental opportunities."
    },
    "Job": {
        "icon": "🛠️",
        "description": "Actual jobs or work applications outside broader opportunity newsletters."
    }
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


def get_credentials():
    if "credentials" not in session:
        return None
    creds_data = session["credentials"]
    return Credentials(
        token=creds_data["token"],
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"],
    )


def decode_email_body(payload):
    body = ""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    elif payload.get("mimeType", "").startswith("multipart/"):
        for part in payload.get("parts", []):
            body = decode_email_body(part)
            if body:
                break
    return body


def fetch_gmail_emails(max_results=40):
    credentials = get_credentials()
    if not credentials:
        return []

    service = build("gmail", "v1", credentials=credentials)
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        q="in:inbox"
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me",
            id=msg_ref["id"],
            format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        body = decode_email_body(msg.get("payload", {}))
        body_truncated = body[:600].strip()

        date_str = headers.get("Date", "")
        try:
            for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %z"]:
                try:
                    parsed = datetime.strptime(date_str[:31].strip(), fmt)
                    date_str = parsed.strftime("%Y-%m-%d %H:%M")
                    break
                except ValueError:
                    continue
        except Exception:
            pass

        emails.append({
            "id": msg_ref["id"],
            "sender": headers.get("From", "Unknown").split("<")[0].strip().strip('"'),
            "sender_email": (re.findall(r"<(.+?)>", headers.get("From", "")) or [headers.get("From", "")])[0],
            "subject": headers.get("Subject", "(no subject)"),
            "body": body_truncated or "(no body)",
            "date": date_str,
        })

    return emails


# ─── GEMINI CATEGORIZATION ───────────────────────────────────────────────────

def ai_categorize_and_summarize(emails):
    if not gemini_client or not emails:
        return [_fallback_enrich(e) for e in emails]

    email_list_text = "\n\n".join([
        f"[{i}] From: {e['sender']} <{e['sender_email']}>\n"
        f"Subject: {e['subject']}\n"
        f"Body: {e['body'][:300]}"
        for i, e in enumerate(emails)
    ])

    prompt = f"""You are an AI inbox organizer for university students.

Analyze each of the following emails and return a JSON array. Each element must have:
- "index": (int) the email's index from the input
- "category": one of "Career", "Resources", "Opportunities", "Job"
  - Career = recruiters, interview invitations, career center, resume events
  - Resources = CAPS, tutoring, financial aid, campus support services, wellness
  - Opportunities = research positions, leadership programs, hackathons, scholarships
  - Job = actual paid jobs, hourly work, part-time employment, RA/TA positions
- "summary": 1-sentence plain English summary of what this email is actually about (max 20 words)
- "priority": integer 1-10 based on urgency and student value
  - 9-10: deadline within days, interview invitation, assessment due
  - 7-8: important opportunity with action needed soon
  - 4-6: useful resource or moderate opportunity
  - 1-3: informational, no action needed, promotional

Return ONLY a valid JSON array. No markdown, no explanation.

Emails:
{email_list_text}
"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        raw = response.text.strip()
        raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw, flags=re.MULTILINE).strip()
        results = json.loads(raw)

        enriched = []
        result_map = {r["index"]: r for r in results}
        for i, email in enumerate(emails):
            r = result_map.get(i, {})
            enriched.append({
                **email,
                "category": r.get("category", "Opportunities"),
                "summary": r.get("summary", email["subject"]),
                "priority": int(r.get("priority", 5)),
                "parsed_date": _parse_date(email["date"]),
            })
        return enriched

    except Exception as e:
        print(f"Gemini categorization error: {e}")
        return [_fallback_enrich(e) for e in emails]


def _parse_date(date_str):
    for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d"]:
        try:
            return datetime.strptime(date_str[:16], fmt)
        except ValueError:
            pass
    return datetime.now()


def _fallback_enrich(email):
    text = f"{email['sender']} {email['subject']} {email['body']}".lower()

    if any(w in text for w in ["caps", "counseling", "tutoring", "resource", "financial hardship", "wellness"]):
        category = "Resources"
    elif any(w in text for w in ["recruit", "interview", "assessment", "career center", "resume"]):
        category = "Career"
    elif any(w in text for w in ["job", "hiring", "shift supervisor", "employment"]):
        category = "Job"
    else:
        category = "Opportunities"

    sentences = [s.strip() for s in email["body"].split(".") if s.strip()]
    summary = (sentences[0] + ".") if sentences else email["subject"]

    score = 5
    if any(w in text for w in ["interview", "assessment", "deadline", "within 5 days", "by friday"]):
        score = 8
    if any(w in text for w in ["offer", "urgent", "today", "immediately"]):
        score = 10

    return {
        **email,
        "category": category,
        "summary": summary[:120],
        "priority": score,
        "parsed_date": _parse_date(email["date"]),
    }


# ─── GEMINI SYNTHESIS ────────────────────────────────────────────────────────

def ai_synthesize(question, emails, category):
    if not gemini_client:
        return _fallback_synthesize(question, emails, category)

    email_context = "\n\n".join([
        f"[Email {e['id']}] From: {e['sender']}\n"
        f"Subject: {e['subject']}\n"
        f"Summary: {e['summary']}\n"
        f"Priority: {e['priority']}/10\n"
        f"Date: {e['date']}"
        for e in emails[:10]
    ])

    prompt = f"""You are an AI assistant helping a university student manage their {category} inbox.

The student asked: "{question}"

Here are the emails in their {category} category:
{email_context}

Answer the student's question helpfully and concisely (2-4 sentences). Be specific — reference actual senders, subjects, and deadlines from the emails above.
At the end of your answer, on a new line, write "CITATIONS:" followed by a comma-separated list of Email IDs you referenced (e.g. "CITATIONS: abc123, def456").
If you didn't reference any specific emails, write "CITATIONS: none"."""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        content = response.text.strip()

        if "CITATIONS:" in content:
            parts = content.split("CITATIONS:")
            answer = parts[0].strip()
            citation_ids_raw = parts[1].strip().split(",")
            citation_ids = [c.strip() for c in citation_ids_raw if c.strip() and c.strip() != "none"]
        else:
            answer = content
            citation_ids = []

        cited_emails = [e for e in emails if str(e["id"]) in citation_ids]
        return {"answer": answer, "citations": cited_emails}

    except Exception as ex:
        print(f"Gemini synthesis error: {ex}")
        return _fallback_synthesize(question, emails, category)


def _fallback_synthesize(question, emails, category):
    q = question.lower()
    if not emails:
        return {"answer": f"No emails in {category} yet.", "citations": []}
    if any(w in q for w in ["urgent", "first", "priority"]):
        top = max(emails, key=lambda x: (x["priority"], x["parsed_date"]))
        return {
            "answer": f'The highest priority email is "{top["subject"]}" from {top["sender"]}.',
            "citations": [top]
        }
    top3 = sorted(emails, key=lambda x: x["priority"], reverse=True)[:3]
    return {
        "answer": f"Here are the top emails in {category}: " + "; ".join([e["subject"] for e in top3]),
        "citations": top3
    }


# ─── DATA HELPERS ────────────────────────────────────────────────────────────

def get_category_emails(emails, category):
    filtered = [e for e in emails if e["category"] == category]
    return sorted(filtered, key=lambda x: (x["priority"], x["parsed_date"]), reverse=True)


def find_email_by_id(emails, email_id):
    return next((e for e in emails if str(e["id"]) == str(email_id)), None)


# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.route("/")
def landing():
    if "credentials" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/login")
def login():
    if not os.path.exists(GOOGLE_CLIENT_SECRETS_FILE):
        flash("Google client secrets file not found.")
        return redirect(url_for("landing"))

    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["oauth_state"] = state
    return redirect(auth_url)


@app.route("/oauth2callback")
def oauth2callback():
    if not os.path.exists(GOOGLE_CLIENT_SECRETS_FILE):
        flash("OAuth credentials not configured.")
        return redirect(url_for("landing"))

    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=session.get("oauth_state"),
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        flash(f"OAuth error: {str(e)}")
        return redirect(url_for("landing"))

    credentials = flow.credentials
    session["credentials"] = credentials_to_dict(credentials)
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/dashboard")
def dashboard():
    if "credentials" not in session:
        return redirect(url_for("landing"))

    raw_emails = fetch_gmail_emails(max_results=40)
    all_emails = ai_categorize_and_summarize(raw_emails)

    session["emails"] = [
        {k: v for k, v in e.items() if k != "parsed_date"}
        for e in all_emails
    ]

    category_cards = []
    for category, meta in CATEGORY_META.items():
        emails = get_category_emails(all_emails, category)
        top = emails[0] if emails else None
        category_cards.append({
            "name": category,
            "icon": meta["icon"],
            "description": meta["description"],
            "count": len(emails),
            "preview": emails[0]["summary"] if emails else "No emails yet.",
            "top_email": top,
        })

    return render_template(
        "index.html",
        category_cards=category_cards,
        total_emails=len(all_emails),
        top_priority=max((e["priority"] for e in all_emails), default=0),
    )


@app.route("/category/<category_name>", methods=["GET", "POST"])
def category_page(category_name):
    if "credentials" not in session:
        return redirect(url_for("landing"))
    if category_name not in CATEGORY_META:
        abort(404)

    cached = session.get("emails", [])
    all_emails = [{**e, "parsed_date": _parse_date(e.get("date", ""))} for e in cached]

    if not all_emails:
        raw_emails = fetch_gmail_emails(max_results=40)
        all_emails = ai_categorize_and_summarize(raw_emails)

    emails = get_category_emails(all_emails, category_name)
    chat_question = ""
    synthesis = None

    if request.method == "POST":
        chat_question = request.form.get("chat_question", "").strip()
        if chat_question:
            synthesis = ai_synthesize(chat_question, emails, category_name)

    return render_template(
        "category.html",
        category_name=category_name,
        category_meta=CATEGORY_META[category_name],
        emails=emails,
        chat_question=chat_question,
        synthesis=synthesis,
        category_meta_all=CATEGORY_META,
    )


@app.route("/email/<email_id>")
def email_detail(email_id):
    if "credentials" not in session:
        return redirect(url_for("landing"))

    cached = session.get("emails", [])
    all_emails = [{**e, "parsed_date": _parse_date(e.get("date", ""))} for e in cached]

    if not all_emails:
        raw_emails = fetch_gmail_emails(max_results=40)
        all_emails = ai_categorize_and_summarize(raw_emails)

    email = find_email_by_id(all_emails, email_id)
    if not email:
        abort(404)

    return render_template(
        "email.html",
        email=email,
        category_meta_all=CATEGORY_META,
    )


if __name__ == "__main__":
    app.run(debug=True)