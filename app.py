import subprocess
import re
from datetime import date
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

FINANCE_EXE = "./finance.exe"
OPENROUTER_API_KEY = "Did you really think you would get my API key?"
OPENROUTER_MODEL = "openai/gpt-4o-mini"

# -------------------------------------------------
# Finance Utilities
# -------------------------------------------------



def run_finance(args):
    """Run finance.exe commands and return stdout."""
    result = subprocess.run(
        [FINANCE_EXE] + args,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def parse_transactions(raw):
    """
    Supports BOTH formats:
    Old:
    2011-04-27 | $56.49 | food | pepperoni | visa

    New (indexed):
    0 | 2011-04-27 | $54 | food | grap | visa
    """
    transactions = []

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        # Remove optional index
        if re.match(r"^\d+\s+\|", line):
            line = line.split("|", 1)[1].strip()

        match = re.match(
            r"(\d{4}-\d{2}-\d{2})\s*\|\s*\$(\-?\d+\.?\d*)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(.+)",
            line
        )

        if match:
            d, amt, cat, desc, method = match.groups()
            transactions.append({
                "date": d.strip(),
                "amount": float(amt),
                "category": cat.strip().lower(),
                "description": desc.strip(),
                "payment_method": method.strip()
            })

    return transactions

# -------------------------------------------------
# AI (RESTORED — READ ONLY, EXPLANATORY)
# -------------------------------------------------

def call_openrouter(user_input, transactions):
    """
    THIS IS THE OLD, GOOD BEHAVIOR.
    The AI:
    - Reads transaction data
    - Explains answers
    - Can do hypotheticals
    - Does NOT modify data
    """

    transactions_text = "\n".join(
        f"{t['date']} | ${t['amount']:.2f} | {t['category']} | {t['description']} | {t['payment_method']}"
        for t in transactions
    ) or "No transactions recorded."

    system_prompt = (
        "You are a personal finance assistant.\n\n"
        "Below is the user's transaction history:\n"
        f"{transactions_text}\n\n"
        "You may ONLY read and analyze this data.\n"
        "You may calculate totals, taxes, averages, trends, and comparisons.\n"
        "You may also solve hypothetical finance or math questions.\n"
        "Always explain your reasoning clearly and in full sentences.\n"
        "Do NOT add, delete, or modify transactions."
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        "temperature": 0.4
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# -------------------------------------------------
# Routes
# -------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

# ---------- AI CHAT ----------
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question", "").strip()
    if not user_input:
        return jsonify({"answer": "Please ask a question."})

    raw = run_finance(["view"])
    transactions = parse_transactions(raw)

    try:
        ai_response = call_openrouter(user_input, transactions)
    except Exception as e:
        return jsonify({"answer": f"Error contacting AI: {str(e)}"})

    return jsonify({"answer": ai_response})

# ---------- TABLE DATA ----------
@app.route("/transactions")
def transactions():
    raw = run_finance(["view"])
    tx = parse_transactions(raw)
    return jsonify(tx)

# ---------- ADD TRANSACTION ----------
@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    data = request.json

    date_val = data.get("date", date.today().isoformat())
    amount = data.get("amount")
    category = data.get("category", "misc")
    description = data.get("description", "purchase")
    payment_method = data.get("payment_method", "manual")

    if amount is None:
        return jsonify({"error": "Amount required"}), 400

    cmd = [
        "add",
        date_val,
        f"{float(amount):.2f}",
        category,
        description,
        payment_method
    ]

    # Debug visibility (as you requested earlier)
    print("RUNNING:", FINANCE_EXE, *cmd)

    run_finance(cmd)
    return jsonify({"status": "ok"})

# ---------- DELETE SPECIFIC TRANSACTION ----------
@app.route("/delete_transaction", methods=["POST"])
def delete_transaction():
    data = request.json
    idx = data.get("idx")
    if idx is None:
        return jsonify({"error": "Missing idx"}), 400

    # Call C++ to delete the transaction
    run_finance(["delete_transaction", str(idx)])
    return jsonify({"status": "ok"})

@app.route("/about")
def about_page():
    return render_template("about.html")
# -------------------------------------------------
# Main
# -------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)
