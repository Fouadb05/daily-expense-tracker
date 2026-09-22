import os
import tempfile
import pytest

os.environ["DATABASE"] = tempfile.mktemp(suffix=".db")

from app import app, init_db, get_db

@pytest.fixture
def client():
    with app.test_client() as client:
        init_db()
        conn = get_db()
        conn.execute("DELETE FROM expenses")
        conn.execute("DELETE FROM budgets")
        conn.commit()
        conn.close()
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_add_expense(client):
    response = client.post("/expenses", json = {
        "amount": 10.0,
        "category": "Food",
    })
    assert response.status_code == 201
    assert "id" in response.get_json()

def test_add_expense_missing_amount(client):
    response = client.post("/expenses", json={
        "category": "Food"
    })
    assert response.status_code == 400
                                   
    response = client.get()


def test_get_expenses_list(client):
    client.post("/expenses", json={"amount": 5.0, "category": "Transport"})
    response = client.get("/expenses")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_missing_expense(client):
    response = client.get("/expenses/999")
    assert response.status_code == 404


def test_delete_expense(client):
    add_response = client.post("/expenses", json={"amount": 5.0, "category": "Bills"})
    expense_id = add_response.get_json()["id"]

    delete_response = client.delete(f"/expenses/{expense_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/expenses/{expense_id}")
    assert get_response.status_code == 404


def test_set_budget(client):
    response = client.post("/budgets", json={
        "category": "Food",
        "monthly_limit": 100,
    })
    assert response.status_code == 201


def test_set_budget_invalid_limit(client):
    response = client.post("/budgets", json={
        "category": "Food",
        "monthly_limit": -10,
    })
    assert response.status_code == 400


def test_summary_no_budget(client):
    client.post("/expenses", json={"amount": 20.0, "category": "Transport"})
    response = client.get("/summary")
    data = response.get_json()

    transport = data["by_category"][0]
    assert transport["category"] == "Transport"
    assert transport["budget"] is None
    assert transport["over_budget"] is False


def test_summary_under_budget(client):
    client.post("/budgets", json={"category": "Food", "monthly_limit": 100})
    client.post("/expenses", json={"amount": 20.0, "category": "Food"})

    response = client.get("/summary")
    data = response.get_json()

    food = data["by_category"][0]
    assert food["budget"] == 100
    assert food["over_budget"] is False


def test_summary_over_budget(client):
    client.post("/budgets", json={"category": "Food", "monthly_limit": 10})
    client.post("/expenses", json={"amount": 20.0, "category": "Food"})

    response = client.get("/summary")
    data = response.get_json()

    food = data["by_category"][0]
    assert food["budget"] == 10
    assert food["over_budget"] is True


def test_summary_updating_budget_replaces_old_one(client):
    client.post("/budgets", json={"category": "Food", "monthly_limit": 50})
    client.post("/budgets", json={"category": "Food", "monthly_limit": 200})
    client.post("/expenses", json={"amount": 100.0, "category": "Food"})

    response = client.get("/summary")
    data = response.get_json()

    food = data["by_category"][0]
    assert food["budget"] == 200