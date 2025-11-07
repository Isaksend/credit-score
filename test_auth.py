"""
Тестовый скрипт для проверки авторизации API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Тест авторизации"""
    print("1. Тест авторизации...")
    
    # Успешная авторизация
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "secret"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Авторизация успешна")
        print(f"   Токен: {token[:50]}...")
        return token
    else:
        print(f"❌ Ошибка авторизации: {response.status_code}")
        print(f"   {response.text}")
        return None

def test_me(token):
    """Тест получения информации о пользователе"""
    print("\n2. Тест получения информации о пользователе...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        user_info = response.json()
        print("✅ Информация получена")
        print(f"   Пользователь: {user_info['username']}")
        print(f"   Роль: {user_info['role']}")
    else:
        print(f"❌ Ошибка: {response.status_code}")

def test_predict_without_auth():
    """Тест предсказания без авторизации"""
    print("\n3. Тест предсказания БЕЗ авторизации...")
    
    response = requests.post(
        f"{BASE_URL}/predict_slim",
        json={
            "R_DEBT_INCOME": 1.78,
            "DEBT": 320000,
            "INCOME": 180000,
            "SAVINGS": 450000
        }
    )
    
    if response.status_code == 401:
        print("✅ Доступ запрещен (как и ожидалось)")
    else:
        print(f"❌ Неожиданный статус: {response.status_code}")

def test_predict_with_auth(token):
    """Тест предсказания с авторизацией"""
    print("\n4. Тест предсказания С авторизацией...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/predict_slim",
        json={
            "R_DEBT_INCOME": 1.78,
            "DEBT": 320000,
            "INCOME": 180000,
            "SAVINGS": 450000
        },
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Предсказание выполнено")
        print(f"   Кредитный скор: {result.get('credit_score', 'N/A')}")
        print(f"   Решение: {result.get('decision', 'N/A')}")
        print(f"   Уровень риска: {result.get('risk_level', 'N/A')}")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(f"   {response.text}")

def test_admin_endpoint(token):
    """Тест эндпоинта для администратора"""
    print("\n5. Тест эндпоинта для администратора...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/model-info", headers=headers)
    
    if response.status_code == 200:
        print("✅ Доступ к информации о модели получен")
    else:
        print(f"❌ Ошибка: {response.status_code}")

def test_wrong_credentials():
    """Тест с неверными учетными данными"""
    print("\n6. Тест с неверными учетными данными...")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "wrong_password"}
    )
    
    if response.status_code == 401:
        print("✅ Неверные учетные данные отклонены (как и ожидалось)")
    else:
        print(f"❌ Неожиданный статус: {response.status_code}")

def main():
    print("="*60)
    print("ТЕСТИРОВАНИЕ АВТОРИЗАЦИИ API")
    print("="*60)
    print("\nУбедитесь, что сервер запущен: uvicorn app.main:app --reload")
    print()
    
    try:
        # Проверка доступности сервера
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("❌ Сервер недоступен. Запустите его командой:")
            print("   cd credit-score && uvicorn app.main:app --reload")
            return
    except requests.exceptions.RequestException:
        print("❌ Сервер недоступен. Запустите его командой:")
        print("   cd credit-score && uvicorn app.main:app --reload")
        return
    
    # Запуск тестов
    token = test_login()
    
    if token:
        test_me(token)
        test_predict_without_auth()
        test_predict_with_auth(token)
        test_admin_endpoint(token)
        test_wrong_credentials()
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)

if __name__ == "__main__":
    main()
