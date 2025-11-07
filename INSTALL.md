# Инструкция по установке

## ✅ Быстрая установка (рекомендуется)

```bash
cd credit-score

# Создать виртуальное окружение
python3 -m venv venv

# Активировать виртуальное окружение
source venv/bin/activate

# Обновить pip
pip install --upgrade pip setuptools wheel

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу: http://localhost:8000

## Вариант 1: Виртуальное окружение (пошагово)

### Создание виртуального окружения

```bash
cd credit-score

# Создать виртуальное окружение
python3 -m venv venv

# Активировать виртуальное окружение
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### Запуск сервера

```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate

# Запустить сервер
uvicorn app.main:app --reload
```

### Деактивация виртуального окружения

```bash
deactivate
```

## Вариант 2: Установка через pipx (для приложений)

```bash
# Установить pipx (если еще не установлен)
brew install pipx

# Установить uvicorn
pipx install uvicorn

# Установить зависимости в системное окружение (не рекомендуется)
pip3 install --user -r requirements.txt
```

## Вариант 3: Использование существующего окружения

Если у вас уже есть виртуальное окружение:

```bash
cd credit-score

# Активировать существующее окружение
source /path/to/your/venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

## Проверка установки

После установки проверьте, что все работает:

```bash
# Запустить сервер
uvicorn app.main:app --reload

# В другом терминале запустить тесты
python test_auth.py
```

## Решение проблем

### Ошибка: "externally-managed-environment"

Это означает, что система защищает системный Python. Используйте виртуальное окружение (Вариант 1).

### Ошибка при установке cryptography

```bash
# Установить зависимости для компиляции
brew install openssl rust

# Попробовать снова
pip install -r requirements.txt
```

### Ошибка при установке bcrypt

```bash
# Установить компилятор
xcode-select --install

# Попробовать снова
pip install -r requirements.txt
```

## Быстрый старт (одной командой)

```bash
cd credit-score && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
echo "✅ Установка завершена! Запустите: uvicorn app.main:app --reload"
```
