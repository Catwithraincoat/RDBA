import pytest
from fastapi.testclient import TestClient
from main import app
from db import Session, engine
from models import Base, Character

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    # Создаем все таблицы перед тестами
    Base.metadata.create_all(bind=engine)
    yield
    # Очищаем базу после тестов
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user_data():
    return {
        "login": "test_user",
        "password": "test_password",
        "name": "Test Character",
        "race": "human",
        "age": 25,
        "relationship": "companion",
    }

@pytest.fixture
def authorized_client(test_user_data):
    # Создаем тестового пользователя
    response = client.post("/signup", json=test_user_data)
    assert response.status_code == 201
    
    # Получаем токен
    response = client.post(
        "/token",
        data={"username": test_user_data["login"], "password": test_user_data["password"]}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Создаем клиент с токеном авторизации
    test_client = TestClient(app)
    test_client.headers = {"Authorization": f"Bearer {token}"}
    return test_client

def test_get_characters():
    response = client.get("/characters")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_character_not_found():
    response = client.get("/characters/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"

def test_login_invalid_credentials():
    response = client.post(
        "/token",
        data={"username": "nonexistent", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_unauthorized_access_journeys():
    response = client.get("/journeys")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_add_journey_unauthorized():
    journey_data = {
        "planet": 1,
        "time": "2024",
        "doctor": 1,
        "description": "Test journey"
    }
    response = client.post("/add_journey", json=journey_data)
    assert response.status_code == 401

def test_signup_success(test_user_data):
    response = client.post("/signup", json=test_user_data)
    assert response.status_code == 201
    assert "user_id" in response.json()

def test_signup_duplicate_login(test_user_data):
    # Первая регистрация
    client.post("/signup", json=test_user_data)
    # Повторная регистрация с тем же логином
    response = client.post("/signup", json=test_user_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_success(test_user_data):
    # Сначала регистрируем пользователя
    client.post("/signup", json=test_user_data)
    
    # Пробуем залогиниться
    response = client.post(
        "/token",
        data={"username": test_user_data["login"], "password": test_user_data["password"]}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

def test_get_journeys_authorized(authorized_client):
    response = authorized_client.get("/journeys")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_journey_success(authorized_client):
    journey_data = {
        "planet": 1,
        "time": "2024",
        "doctor": 1,
        "description": "Test journey"
    }
    response = authorized_client.post("/add_journey", json=journey_data)
    assert response.status_code == 201
    assert "journey_id" in response.json()

def test_get_character_success():
    # Предполагаем, что в базе есть персонаж с id=1
    response = client.get("/characters/1")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "race" in response.json()

def test_invalid_journey_data(authorized_client):
    invalid_journey_data = {
        "planet": "invalid",  # должно быть число
        "time": "2024",
        "doctor": 1,
        "description": "Test journey"
    }
    response = authorized_client.post("/add_journey", json=invalid_journey_data)
    assert response.status_code == 422

def test_get_characters_empty():
    # Очищаем базу данных перед тестом
    session = Session()
    session.query(Character).delete()
    session.commit()
    session.close()
    
    response = client.get("/characters")
    assert response.status_code == 200
    assert response.json() == []
