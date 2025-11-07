# 🏦 Credit Scoring API с авторизацией

AI-система кредитного скоринга для малых ритейлеров с JWT авторизацией.

## 🚀 Быстрый старт

```bash
cd credit-score
./start.sh
```

Или вручную:

```bash
cd credit-score
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Сервер запустится на:** http://localhost:8000

## 🔐 Авторизация

API защищен JWT токенами. Для доступа к эндпоинтам предсказаний нужна авторизация.

### Тестовые учетные данные

| Пользователь | Пароль   | Роль  | Доступ                          |
|--------------|----------|-------|---------------------------------|
| admin        | secret   | admin | Полный доступ ко всем эндпоинтам |
| user         | password | user  | Доступ к предсказаниям          |

### Получение токена

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}'
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 📡 API Эндпоинты

### Публичные (без авторизации)
- `GET /` - Информация об API
- `GET /health` - Проверка здоровья
- `GET /features` - Список признаков
- `GET /statistics` - Статистика
- `POST /auth/login` - Авторизация

### Защищенные (требуется токен)
- `POST /predict` - Полное предсказание
- `POST /predict_slim` - Упрощенное предсказание (12 признаков)
- `POST /predict/default` - Предсказание дефолта
- `POST /predict/score` - Предсказание скора
- `POST /predict/batch` - Пакетное предсказание
- `GET /auth/me` - Информация о текущем пользователе

### Только для администраторов
- `GET /model-info` - Информация о модели

## 💡 Примеры использования

### Python

```python
import requests

# 1. Авторизация
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "secret"}
)
token = response.json()["access_token"]

# 2. Предсказание
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/predict_slim",
    json={
        "R_DEBT_INCOME": 1.78,
        "DEBT": 320000,
        "INCOME": 180000,
        "SAVINGS": 450000
    },
    headers=headers
)
print(response.json())
```

### cURL

```bash
# Получить токен
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}' | jq -r '.access_token')

# Сделать предсказание
curl -X POST "http://localhost:8000/predict_slim" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "R_DEBT_INCOME": 1.78,
    "DEBT": 320000,
    "INCOME": 180000,
    "SAVINGS": 450000
  }'
```

### JavaScript

```javascript
// Авторизация
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'secret'})
});
const {access_token} = await response.json();

// Предсказание
const result = await fetch('http://localhost:8000/predict_slim', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    R_DEBT_INCOME: 1.78,
    DEBT: 320000,
    INCOME: 180000,
    SAVINGS: 450000
  })
});
console.log(await result.json());
```

## 🧪 Тестирование

```bash
source venv/bin/activate
python test_auth.py
```

## 📚 Документация

- 📖 **Swagger UI**: http://localhost:8000/docs
- 📘 **ReDoc**: http://localhost:8000/redoc
- 🚀 **Быстрый старт**: [QUICKSTART.md](QUICKSTART.md)
- 🔐 **Примеры авторизации**: [AUTH_EXAMPLES.md](AUTH_EXAMPLES.md)
- 📦 **Установка**: [INSTALL.md](INSTALL.md)

## 🏗️ Структура проекта

```
credit-score/
├── app/
│   ├── main.py              # Основное приложение FastAPI
│   ├── auth.py              # Модуль авторизации (JWT)
│   ├── predictor.py         # Модуль предсказаний
│   └── generate_password.py # Генератор паролей
├── models/                  # ML модели
├── venv/                    # Виртуальное окружение
├── requirements.txt         # Зависимости Python
├── start.sh                 # Скрипт быстрого запуска
├── test_auth.py            # Тесты авторизации
└── README.md               # Эта инструкция
```

## 🔧 Добавление новых пользователей

```bash
source venv/bin/activate
python app/generate_password.py
```

Скопируйте сгенерированный хеш в `app/auth.py` в словарь `USERS_DB`.

## ⚠️ Безопасность для продакшена

1. **Измените SECRET_KEY** в `app/auth.py`
2. **Используйте переменные окружения** для секретов
3. **Настройте HTTPS**
4. **Используйте реальную БД** вместо словаря пользователей
5. **Ограничьте CORS** для конкретных доменов
6. **Увеличьте сложность паролей**

## 📋 Требования

- Python 3.9+
- FastAPI
- JWT (python-jose)
- Passlib + bcrypt
- scikit-learn
- pandas, numpy

## 🐛 Решение проблем

### Ошибка "externally-managed-environment"
Используйте виртуальное окружение (см. [INSTALL.md](INSTALL.md))

### Ошибка при установке пакетов
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Сервер не запускается
Проверьте, что виртуальное окружение активировано:
```bash
source venv/bin/activate
```

## 📝 Лицензия

MIT

## 👥 Авторы

Credit Scoring API Team
