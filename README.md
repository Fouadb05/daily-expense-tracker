# Daily Expense Tracker

A personal budgeting tool with a Python/Flask/SQLite REST API backend and a simple HTML/JavaScript frontend.

## Features
- Add, view, edit, and delete expenses
- Input validation
- Spending summaries by category and by month
- Monthly budgets per category, with over-budget warnings
- Simple frontend to manage everything in the browser

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
| POST | /budgets | Set (or update) a monthly budget for a category |

## Setup

1. Create and activate a virtual environment:
\`\`\`
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate     # Mac/Linux
\`\`\`

2. Install dependencies:
\`\`\`
pip install -r requirements.txt
\`\`\`

3. Start the API:
\`\`\`
python app.py
\`\`\`

4. Open `index.html` directly in your browser to use the app.

## Running backend tests
\`\`\`
pytest
\`\`\`

## Project structure
- `app.py` — Flask API and database logic
- `test_app.py` — pytest tests for the API
- `index.html` — frontend page
- `style.css` — frontend styling
- `requirements.txt` — Python dependencies