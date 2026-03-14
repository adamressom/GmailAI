from flask import Flask, render_template, request

app = Flask(__name__)

# Simple in-memory history for demo purposes
topic_history = []


def build_response(topic, style, difficulty):
    topic_lower = topic.lower().strip()

    explanations = {
        "derivatives": {
            "beginner": {
                "steps": "A derivative tells you how fast something is changing. Start by thinking of it like the slope of a curve at one point.",
                "visual": "Picture a curve on a graph. The derivative is the slope of the line that just touches the curve at one point.",
                "practice": "A derivative measures rate of change. Start with easy examples and compare how steep the graph looks."
            },
            "intermediate": {
                "steps": "A derivative gives the instantaneous rate of change. Practice using the power rule on simple polynomials first.",
                "visual": "Imagine zooming in on a curve until it looks like a straight line. That line's slope is the derivative.",
                "practice": "Think of derivatives as a way to measure how a function changes at each point."
            },
            "advanced": {
                "steps": "Use the limit definition to understand why the derivative works, then connect that to shortcut rules like the power rule.",
                "visual": "See the derivative as the limit of secant slopes becoming one tangent slope.",
                "practice": "Connect the graphical meaning of slope to the formal limit definition of the derivative."
            },
            "practice_question": "Find the derivative of x^2."
        },
        "fractions": {
            "beginner": {
                "steps": "Start by finding a common denominator. Then rewrite each fraction so the denominators match before combining them.",
                "visual": "Think of each fraction as pieces of the same pizza. You need the same slice size before you can combine them.",
                "practice": "Focus on finding a common denominator before you add or subtract fractions."
            },
            "intermediate": {
                "steps": "Simplify fractions where possible, then use the least common denominator to make the arithmetic cleaner.",
                "visual": "Imagine converting all fraction pieces into equal-size parts before doing the operation.",
                "practice": "Practice adding and subtracting fractions with different denominators."
            },
            "advanced": {
                "steps": "Work efficiently by finding the least common denominator and simplifying at every stage.",
                "visual": "View equivalent fractions as different names for the same amount.",
                "practice": "Challenge yourself with mixed numbers and multi-step fraction problems."
            },
            "practice_question": "Add 1/3 + 1/6."
        },
        "loops": {
            "beginner": {
                "steps": "A loop repeats code. Focus on three things: where it starts, when it stops, and what changes each time.",
                "visual": "Think of a loop like going around a track again and again until a stopping rule says stop.",
                "practice": "Trace a short loop by hand and write down the value after each repetition."
            },
            "intermediate": {
                "steps": "Pay attention to the loop condition and the update step, because those control how many times it runs.",
                "visual": "Imagine a counter climbing step by step until it reaches a limit.",
                "practice": "Practice predicting how many times a loop runs before checking with code."
            },
            "advanced": {
                "steps": "Analyze initialization, condition, and update carefully. Then watch for off-by-one errors.",
                "visual": "View the loop as a state machine that moves from one value to the next.",
                "practice": "Try tracing nested loops and counting total iterations."
            },
            "practice_question": "What does a loop from i = 0 to i < 3 print if it prints i each time?"
        },
        "probability": {
            "beginner": {
                "steps": "Probability is how likely something is to happen. Start with favorable outcomes over total outcomes.",
                "visual": "Imagine a bag of colored marbles. Probability is the fraction of marbles that match what you want.",
                "practice": "Count the total possible outcomes first, then count the successful ones."
            },
            "intermediate": {
                "steps": "Use formulas carefully and decide whether outcomes are independent or dependent.",
                "visual": "Use a tree diagram to map all possible outcomes.",
                "practice": "Practice simple coin, dice, and card problems."
            },
            "advanced": {
                "steps": "Pay attention to conditional probability, independence, and whether order matters.",
                "visual": "Represent events as sets and overlaps to understand intersections and unions.",
                "practice": "Try multi-step problems involving combinations and conditional events."
            },
            "practice_question": "What is the probability of rolling a 4 on a fair six-sided die?"
        }
    }

    if topic_lower in explanations:
        explanation = explanations[topic_lower][difficulty][style]
        practice_question = explanations[topic_lower]["practice_question"]
    else:
        if style == "steps":
            explanation = f"A good first step for {topic} is to review the basics, define the main idea, and solve one simple example."
        elif style == "visual":
            explanation = f"For {topic}, try drawing a diagram, graph, or picture so you can see the concept instead of only reading about it."
        else:
            explanation = f"For {topic}, start with one easy practice problem before moving to harder ones."

        if difficulty == "beginner":
            explanation += " Since you chose beginner, keep the example very simple."
        elif difficulty == "intermediate":
            explanation += " Since you chose intermediate, try one example and one slightly harder follow-up."
        else:
            explanation += " Since you chose advanced, connect the idea to formal rules or definitions."

        practice_question = f"Write one simple practice problem related to {topic} and solve it step by step."

    style_labels = {
        "steps": "Step-by-step explanation",
        "visual": "Visual explanation",
        "practice": "Practice-based explanation"
    }

    difficulty_labels = {
        "beginner": "Beginner",
        "intermediate": "Intermediate",
        "advanced": "Advanced"
    }

    return {
        "topic": topic,
        "style_label": style_labels[style],
        "difficulty_label": difficulty_labels[difficulty],
        "explanation": explanation,
        "practice_question": practice_question
    }


@app.route("/")
def home():
    return render_template(
        "index.html",
        result=None,
        history=topic_history[-5:]
    )


@app.route("/help", methods=["POST"])
def help_page():
    topic = request.form.get("topic", "").strip()
    style = request.form.get("style", "steps")
    difficulty = request.form.get("difficulty", "beginner")

    if not topic:
        return render_template(
            "index.html",
            result={
                "topic": "",
                "style_label": "",
                "difficulty_label": "",
                "explanation": "Please enter a topic first.",
                "practice_question": ""
            },
            history=topic_history[-5:]
        )

    topic_history.append(topic)
    result = build_response(topic, style, difficulty)

    return render_template(
        "index.html",
        result=result,
        history=topic_history[-5:]
    )


if __name__ == "__main__":
    app.run(debug=True)