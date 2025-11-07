# Примеры использования API с авторизацией

## Тестовые учетные данные

### Администратор (полный доступ)
- **Username:** `admin`
- **Password:** `secret`

### Пользователь (ограниченный доступ)
- **Username:** `user`
- **Password:** `password`

## 1. Авторизация

### Получение токена
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secret"
  }'
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Проверка текущего пользователя
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 2. Использование защищенных эндпоинтов

### Предсказание (требуется авторизация)
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "INCOME": 180000,
      "SAVINGS": 450000,
      "DEBT": 320000,
      "R_DEBT_INCOME": 1.78
    }
  }'
```

### Упрощенное предсказание (требуется авторизация)
```bash
curl -X POST "http://localhost:8000/predict_slim" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "R_DEBT_INCOME": 1.78,
    "DEBT": 320000,
    "INCOME": 180000,
    "SAVINGS": 450000
  }'
```

### Информация о модели (требуется роль admin)
```bash
curl -X GET "http://localhost:8000/model-info" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 3. Использование в Python

```python
import requests

# 1. Авторизация
login_url = "http://localhost:8000/auth/login"
login_data = {
    "username": "admin",
    "password": "secret"
}

response = requests.post(login_url, json=login_data)
token = response.json()["access_token"]

# 2. Использование токена для запросов
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 3. Предсказание
predict_url = "http://localhost:8000/predict_slim"
client_data = {
    "R_DEBT_INCOME": 1.78,
    "DEBT": 320000,
    "INCOME": 180000,
    "SAVINGS": 450000
}

response = requests.post(predict_url, json=client_data, headers=headers)
print(response.json())
```

## 4. Использование в JavaScript/Fetch

```javascript
// 1. Авторизация
async function login() {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: 'admin',
      password: 'secret'
    })
  });
  
  const data = await response.json();
  return data.access_token;
}

// 2. Предсказание с токеном
async function predict(token) {
  const response = await fetch('http://localhost:8000/predict_slim', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      R_DEBT_INCOME: 1.78,
      DEBT: 320000,
      INCOME: 180000,
      SAVINGS: 450000
    })
  });
  
  return await response.json();
}

// Использование
const token = await login();
const result = await predict(token);
console.log(result);
```

## 5. Swagger UI

Откройте http://localhost:8000/docs для интерактивной документации.

**Как использовать авторизацию в Swagger:**
1. Нажмите кнопку "Authorize" (замок) в правом верхнем углу
2. Сначала выполните запрос `/auth/login` чтобы получить токен
3. Скопируйте значение `access_token` из ответа
4. Нажмите "Authorize" и вставьте токен в поле "Value"
5. Нажмите "Authorize" и "Close"
6. Теперь все запросы будут использовать этот токен

## Обработка ошибок

### 401 Unauthorized
```json
{
  "detail": "Не удалось проверить учетные данные"
}
```
**Решение:** Получите новый токен через `/auth/login`

### 403 Forbidden
```json
{
  "detail": "Недостаточно прав доступа"
}
```
**Решение:** Используйте учетную запись с правами администратора

## Безопасность

⚠️ **Важно для продакшена:**
1. Измените `SECRET_KEY` в `app/auth.py` на случайную строку
2. Используйте переменные окружения для хранения секретов
3. Настройте HTTPS
4. Используйте реальную базу данных вместо словаря
5. Настройте CORS для конкретных доменов
