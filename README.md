# Daily Expense Tracker

A personal budgeting API built with Python, Flask, and SQLite.

## Features
- Add, view, update, and delete expenses
- Input validation
- Spending summaries by category and by month
- Optional monthly budgets per category, with over-budget flags

## Endpoints
| Method | URL | Description |
|---|---|---|
| POST | /expenses | Add an expense |
| GET | /expenses | List all expenses |
| GET | /expenses/<id> | Get one expense |
| PUT | /expenses/<id> | Update an expense |
| DELETE | /expenses/<id> | Delete an expense |
| GET | /summary | Spending totals by category |
| GET | /summary?month=YYYY-MM | Spending totals for one month |
| POST | /budgets | Set a monthly budget for a category |

## Setup
\`\`\`
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
python app.py
\`\`\`

## Running tests
\`\`\`
pytest
\`\`\`