import sqlite3
from datetime import date
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
import os
DATABASE = os.environ.get("DATABASE", "expenses.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
        category TEXT PRIMARY KEY,
        monthly_limit REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def validate_expense_data(data):
    if data is None:
        return "No JSON data recieved"

    amount = data.get("amount")
    category = data.get("category")

    if amount is None:
        return "amount is required"
    if not isinstance(amount, (int, float)):
        return "amount must be a number"
    if amount <= 0:
        return "amount must be greater than 0"
    if not category:
        return "category is required"
    if not isinstance(category, (str)):
        return "Category is required to be text"
    if category.strip().isdigit():
        return "category cannot be only numbers"


    return None


@app.route("/")
def home():
    return "Expense Tracker is running!"

@app.route("/expenses", methods=["POST"])
def add_expense():
    data = request.get_json()

    error = validate_expense_data(data)
    if error:
        return jsonify({"error": error}), 400

    amount = data.get("amount")
    category = data.get("category")
    description = data.get("description", "")
    expense_date = data.get("date", date.today().isoformat())

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
        (amount, category, description, expense_date),

    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": new_id, "message": "Expense added"}), 201

@app.route("/expenses", methods=["GET"])
def get_expenses():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM expenses ORDER BY date DESC, id DESC"
    ).fetchall()
    conn.close()

    expenses = [dict(row) for row in rows]
    return jsonify(expenses)

@app.route("/expenses/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify(dict(row))


@app.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    conn = get_db()
    cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Expense not found"}), 404
    return ({"message": "Expense deleted"})


@app.route("/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()

    if row is None:
        conn.close()
        return jsonify({"error": "Expense not found"}), 404

    data = request.get_json()
    error = validate_expense_data({
        "amount": data.get("amount", row["amount"]),
        "category": data.get("category", row["category"])
    })

    if error:
        conn.close()
        return jsonify({"error": error}), 400


    amount = data.get("amount", row["amount"])
    category = data.get("category", row["category"])
    description = data.get("description", row["description"])
    expense_date = data.get("date", row["date"])

    conn.execute("UPDATE expenses SET amount = ?, category = ?, description = ?, date = ? WHERE id = ?",
        (amount, category, description, expense_date, expense_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Expense updated"})


@app.route("/summary", methods=["GET"])
def get_summary():
    month = request.args.get("month")

    conn = get_db()
    if month:
        rows = conn.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date LIKE ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (f"{month}%",),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
            """
        ).fetchall()
    conn.close()

    conn2 = get_db()
    budget_rows = conn2.execute("SELECT * FROM budgets").fetchall()
    conn2.close()
    budgets = {row["category"]: row["monthly_limit"] for row in budget_rows}
    by_category = []
    for row in rows:
        entry = dict(row)
        limit = budgets.get(entry["category"])
        entry["budget"] = limit
        entry["over_budget"] = limit is not None and entry["total"] > limit
        by_category.append(entry)


    grand_total = sum(row["total"] for row in by_category)

    return jsonify({
        "month": month if month else "all time",
        "total": grand_total,
        "by_category": by_category,
    })


@app.route("/budgets", methods=["POST"])
def set_budget():
    data = request.get_json()
    category = data.get("category")
    monthly_limit = data.get("monthly_limit")

    if not category or not isinstance(category, str):
        return jsonify({"error": "category is required and must be text"}), 400
    if not isinstance(monthly_limit, (int, float)) or monthly_limit <= 0:
        return jsonify({"error": "monthly_limit must be a positive number"}), 400

    conn = get_db()
    conn.execute(
        """
        INSERT INTO budgets (category, monthly_limit) VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
        """,
        (category, monthly_limit),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Budget set"}), 201

if __name__ == "__main__":
    init_db()
    app.run(debug=True)