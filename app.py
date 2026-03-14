from flask import Flask, render_template, request, abort
from datetime import datetime

app = Flask(__name__)

EMAILS = [
    {
        "id": 1,
        "sender": "Google Student Recruiting",
        "sender_email": "studentrecruiting@google.com",
        "subject": "Software Engineering Internship Interview Invitation",
        "body": "Hi Adam, we reviewed your application and would like to invite you to interview for our Summer Software Engineering Internship. Please choose an interview time by Friday at 5 PM.",
        "date": "2026-03-13 10:30"
    },
    {
        "id": 2,
        "sender": "JHU Career Center",
        "sender_email": "careercenter@jhu.edu",
        "subject": "Resume Review Week and Internship Support Resources",
        "body": "The Career Center is hosting resume reviews, mock interviews, and internship search workshops this week. Students are encouraged to book appointments early because slots fill quickly.",
        "date": "2026-03-12 09:15"
    },
    {
        "id": 3,
        "sender": "Counseling Center",
        "sender_email": "caps@university.edu",
        "subject": "CAPS Drop-In Hours and Mental Health Resources",
        "body": "CAPS is offering expanded drop-in counseling hours this month. Students can also access workshops, wellness coaching, and urgent support if they feel overwhelmed.",
        "date": "2026-03-11 13:05"
    },
    {
        "id": 4,
        "sender": "Undergraduate Research Office",
        "sender_email": "research@university.edu",
        "subject": "Paid Summer Research Opportunity in Data Science",
        "body": "Students interested in machine learning and data science are invited to apply for a funded summer research position. The application deadline is next Tuesday and selected students will work with faculty mentors.",
        "date": "2026-03-13 11:40"
    },
    {
        "id": 5,
        "sender": "Math Tutoring Center",
        "sender_email": "tutoring@university.edu",
        "subject": "Free Calculus and Physics Tutoring Available",
        "body": "The tutoring center provides free support for calculus, physics, chemistry, and programming. Walk-in tutoring begins this week and students may reserve one-on-one appointments online.",
        "date": "2026-03-10 16:00"
    },
    {
        "id": 6,
        "sender": "Starbucks Hiring Team",
        "sender_email": "jobs@starbucks.com",
        "subject": "Your Shift Supervisor Application Status",
        "body": "Thank you for applying for the Shift Supervisor role. Our team is reviewing your application and may contact you for next steps if your experience aligns with the position.",
        "date": "2026-03-09 18:20"
    },
    {
        "id": 7,
        "sender": "Amazon Student Programs",
        "sender_email": "university-recruiting@amazon.com",
        "subject": "Complete Your Online Assessment Within 5 Days",
        "body": "You have been selected to move forward in the internship process. Please complete the online assessment within 5 days to remain under consideration.",
        "date": "2026-03-13 12:10"
    },
    {
        "id": 8,
        "sender": "Leadership Programs Office",
        "sender_email": "leadership@university.edu",
        "subject": "Apply for Emerging Student Leaders Program",
        "body": "Applications are now open for the Emerging Student Leaders Program. Participants will receive mentorship, leadership training, and access to campus networking events.",
        "date": "2026-03-12 15:35"
    },
    {
        "id": 9,
        "sender": "Handshake",
        "sender_email": "jobs@handshake.com",
        "subject": "8 New Opportunities Match Your Profile",
        "body": "Based on your profile, we found new opportunities in software engineering, data science, and machine learning. Several roles are open to first- and second-year students.",
        "date": "2026-03-13 08:50"
    },
    {
        "id": 10,
        "sender": "University Housing",
        "sender_email": "housing@university.edu",
        "subject": "Resident Assistant Information Session",
        "body": "Students interested in becoming Resident Assistants are invited to attend an information session next week. The session will explain responsibilities, benefits, and the application timeline.",
        "date": "2026-03-11 17:25"
    },
    {
        "id": 11,
        "sender": "Meta University Programs",
        "sender_email": "meta@recruiting.com",
        "subject": "Application Received for Software Engineer Internship",
        "body": "We received your application. If selected, the next stages may include an assessment and a recruiter conversation. Thank you for your interest in Meta University Programs.",
        "date": "2026-03-10 11:45"
    },
    {
        "id": 12,
        "sender": "Financial Aid Office",
        "sender_email": "finaid@university.edu",
        "subject": "Resource Reminder: Emergency Funding and Support Services",
        "body": "Students facing financial hardship may be eligible for emergency grants, textbook support, and short-term assistance. Visit the student support portal for details and application instructions.",
        "date": "2026-03-12 10:10"
    }
]

CATEGORY_META = {
    "Career": {
        "icon": "💼",
        "description": "Recruiter emails, internship process updates, and career-related communication."
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


def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M")


def summarize_email(body):
    sentences = [s.strip() for s in body.split(".") if s.strip()]
    if not sentences:
        return body
    if len(sentences) == 1:
        return sentences[0] + "."
    return sentences[0] + ". " + sentences[1] + "."


def categorize_email(email):
    text = f"{email['sender']} {email['subject']} {email['body']}".lower()

    career_keywords = [
        "recruit", "interview", "assessment", "application received",
        "career center", "resume", "mock interview"
    ]
    resource_keywords = [
        "caps", "counseling", "tutoring", "resource", "support services",
        "financial hardship", "emergency grants", "wellness", "drop-in"
    ]
    opportunity_keywords = [
        "opportunity", "research", "leadership", "program", "mentorship",
        "summer position", "apply", "student leaders", "handshake",
        "internship", "funded"
    ]
    job_keywords = [
        "job", "hiring", "shift supervisor", "position", "employment", "resident assistant"
    ]

    if any(word in text for word in resource_keywords):
        return "Resources"
    if any(word in text for word in career_keywords):
        return "Career"
    if any(word in text for word in job_keywords):
        return "Job"
    if any(word in text for word in opportunity_keywords):
        return "Opportunities"

    return "Opportunities"


def compute_priority(email, category):
    text = f"{email['subject']} {email['body']}".lower()
    score = 1

    urgent_terms = [
        "by friday", "deadline", "within 5 days", "next tuesday",
        "this week", "choose", "complete", "apply"
    ]
    for term in urgent_terms:
        if term in text:
            score += 2

    if "interview" in text:
        score += 4
    if "assessment" in text:
        score += 3
    if "paid" in text or "funded" in text:
        score += 2
    if "free" in text:
        score += 1
    if "support" in text:
        score += 1

    if category == "Career":
        score += 2
    elif category == "Opportunities":
        score += 2
    elif category == "Resources":
        score += 1

    return min(score, 10)


def enrich_emails():
    enriched = []
    for email in EMAILS:
        category = categorize_email(email)
        summary = summarize_email(email["body"])
        priority = compute_priority(email, category)
        enriched.append({
            **email,
            "category": category,
            "summary": summary,
            "priority": priority,
            "parsed_date": parse_date(email["date"])
        })

    enriched.sort(key=lambda x: x["parsed_date"], reverse=True)
    return enriched


def get_category_counts(emails):
    counts = {category: 0 for category in CATEGORY_META}
    for email in emails:
        counts[email["category"]] += 1
    return counts


def get_category_emails(emails, category):
    filtered = [e for e in emails if e["category"] == category]
    filtered.sort(key=lambda x: (x["priority"], x["parsed_date"]), reverse=True)
    return filtered


def find_email_by_id(emails, email_id):
    for email in emails:
        if email["id"] == email_id:
            return email
    return None


def top_email(emails):
    if not emails:
        return None
    return sorted(emails, key=lambda x: (x["priority"], x["parsed_date"]), reverse=True)[0]


def synthesize_category_question(question, emails, category):
    q = question.lower().strip()

    if not q:
        return {
            "answer": "Ask something like “Which one is most urgent?”, “What resources should I use first?”, or “Which opportunity looks strongest?”",
            "citations": []
        }

    if not emails:
        return {
            "answer": f"There are no emails in the {category} category yet.",
            "citations": []
        }

    if "urgent" in q or "first" in q or "priority" in q:
        top = top_email(emails)
        return {
            "answer": (
                f'The email I would prioritize first is "{top["subject"]}" from {top["sender"]} because it has the strongest action language and one of the highest priority scores.'
            ),
            "citations": [top]
        }

    if "best opportunity" in q or "strongest opportunity" in q or "best one" in q:
        scored = sorted(emails, key=lambda x: (x["priority"], x["parsed_date"]), reverse=True)
        best = scored[0]
        return {
            "answer": (
                f'The strongest option appears to be "{best["subject"]}" from {best["sender"]}. It stands out because it offers clearer next steps and stronger potential value for the student.'
            ),
            "citations": [best]
        }

    if "resource" in q or "help" in q or "support" in q:
        matching = []
        for email in emails:
            text = f"{email['subject']} {email['body']}".lower()
            if any(word in text for word in ["tutoring", "caps", "support", "grant", "wellness", "financial"]):
                matching.append(email)

        if matching:
            return {
                "answer": "The most relevant support resources here are tutoring, counseling, and financial support services. These appear to directly help students who are academically or personally overwhelmed.",
                "citations": matching[:3]
            }

    if "summarize" in q or "summary" in q or "synthesize" in q:
        selected = emails[:3]
        answer_lines = []
        for email in selected:
            answer_lines.append(f'• {email["sender"]}: {email["summary"]}')
        return {
            "answer": "Here is a quick synthesis of the most important emails in this category:\n" + "\n".join(answer_lines),
            "citations": selected
        }

    if "deadline" in q or "when" in q:
        matching = []
        for email in emails:
            text = f"{email['subject']} {email['body']}".lower()
            if any(word in text for word in ["friday", "tuesday", "within 5 days", "this week", "deadline"]):
                matching.append(email)

        if matching:
            return {
                "answer": "The category includes at least one time-sensitive email that should be reviewed soon because it mentions a deadline or a limited response window.",
                "citations": matching[:2]
            }

    selected = emails[:2]
    return {
        "answer": (
            f'In the {category} category, I would scan the highest-priority emails first, compare deadlines and action steps, and then follow up on the items that give the most concrete support or opportunity.'
        ),
        "citations": selected
    }


@app.route("/")
def dashboard():
    all_emails = enrich_emails()
    category_counts = get_category_counts(all_emails)

    category_cards = []
    for category, meta in CATEGORY_META.items():
        emails = get_category_emails(all_emails, category)
        preview = emails[0]["summary"] if emails else "No emails in this category yet."
        category_cards.append({
            "name": category,
            "icon": meta["icon"],
            "description": meta["description"],
            "count": len(emails),
            "preview": preview,
            "top_email": emails[0] if emails else None
        })

    total_emails = len(all_emails)
    top_priority = max([e["priority"] for e in all_emails]) if all_emails else 0

    return render_template(
        "index.html",
        category_cards=category_cards,
        total_emails=total_emails,
        top_priority=top_priority
    )


@app.route("/category/<category_name>", methods=["GET", "POST"])
def category_page(category_name):
    if category_name not in CATEGORY_META:
        abort(404)

    all_emails = enrich_emails()
    emails = get_category_emails(all_emails, category_name)

    chat_question = ""
    synthesis = None

    if request.method == "POST":
        chat_question = request.form.get("chat_question", "")
        synthesis = synthesize_category_question(chat_question, emails, category_name)

    return render_template(
        "category.html",
        category_name=category_name,
        category_meta=CATEGORY_META[category_name],
        emails=emails,
        chat_question=chat_question,
        synthesis=synthesis,
        category_meta_all=CATEGORY_META
    )


@app.route("/email/<int:email_id>")
def email_detail(email_id):
    all_emails = enrich_emails()
    email = find_email_by_id(all_emails, email_id)

    if not email:
        abort(404)

    return render_template(
        "email.html",
        email=email,
        category_meta_all=CATEGORY_META
    )


if __name__ == "__main__":
    app.run(debug=True)