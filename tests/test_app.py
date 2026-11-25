from datetime import date, timedelta

import pytest

from app import calculate_streak, create_app, db


@pytest.fixture()
def client():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
    return app.test_client()


def register(client):
    return client.post("/api/auth/register", json={
        "name": "Pessoa Teste",
        "email": "teste@example.com",
        "password": "segredo123",
    })


def test_guest_sees_catalog_but_protected_content_requires_login(client):
    home = client.get("/")
    assert home.status_code == 200
    assert b"0 XP" in home.data
    assert client.get("/modulos").status_code == 200
    detail = client.get("/modulos/conjuntos-logica")
    assert detail.status_code == 302
    assert "/entrar" in detail.headers["Location"]
    assert client.get("/quiz").status_code == 302
    assert client.get("/api/quizzes/conjuntos-logica").status_code == 401


def test_new_account_starts_at_zero_with_only_first_module_unlocked(client):
    response = register(client)
    assert response.status_code == 201
    assert response.get_json()["stats"]["xp"] == 0
    assert response.get_json()["stats"]["streak"] == 0
    me = client.get("/api/auth/me").get_json()
    assert me["modules"][0]["unlocked"] is True
    assert me["modules"][1]["unlocked"] is False
    assert client.get("/modulos/conjuntos-logica").status_code == 200
    assert client.get("/modulos/espacos-euclidianos").status_code == 302
    dashboard = client.get("/painel")
    assert dashboard.status_code == 200
    assert b"0 XP" in dashboard.data


def test_quiz_is_server_corrected_awards_xp_and_unlocks_next_module(client):
    register(client)
    quiz = client.get("/api/quizzes/conjuntos-logica")
    assert quiz.status_code == 200
    assert "answer" not in quiz.get_json()["questions"][0]

    submitted = client.post("/api/quizzes/conjuntos-logica/submit", json={
        "answers": [1, 2, 1],
    })
    result = submitted.get_json()
    assert submitted.status_code == 200
    assert result["percentage"] == 100
    assert result["xp_earned"] == 150
    assert result["stats"]["xp"] == 150
    assert result["stats"]["streak"] == 1
    assert result["modules"][1]["unlocked"] is True

    me = client.get("/api/auth/me").get_json()
    assert me["progress"][0]["completed"] is True
    assert client.get("/modulos/espacos-euclidianos").status_code == 200


def test_repeating_with_lower_score_does_not_farm_xp(client):
    register(client)
    client.post("/api/quizzes/conjuntos-logica/submit", json={"answers": [1, 2, 1]})
    repeated = client.post("/api/quizzes/conjuntos-logica/submit", json={"answers": [0, 0, 0]})
    assert repeated.status_code == 200
    assert repeated.get_json()["xp_earned"] == 0
    assert repeated.get_json()["stats"]["xp"] == 150


def test_rejects_incomplete_quiz(client):
    register(client)
    response = client.post("/api/quizzes/conjuntos-logica/submit", json={"answers": [1]})
    assert response.status_code == 400


def test_streak_counts_consecutive_days_and_expires_after_gap():
    today = date(2026, 11, 23)
    streak, longest = calculate_streak(
        [today, today - timedelta(days=1), today - timedelta(days=2), today - timedelta(days=5)],
        today=today,
    )
    assert streak == 3
    assert longest == 3
    expired, _ = calculate_streak([today - timedelta(days=3)], today=today)
    assert expired == 0
