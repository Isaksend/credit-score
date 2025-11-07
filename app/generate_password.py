"""
Утилита для генерации хешей паролей
Используйте этот скрипт для создания новых пользователей
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_password_hash(password: str) -> str:
    """Генерация хеша пароля"""
    return pwd_context.hash(password)

if __name__ == "__main__":
    print("=== Генератор хешей паролей ===\n")
    
    # Примеры
    passwords = {
        "admin": "secret",
        "user": "password"
    }
    
    print("Текущие пароли:")
    for username, password in passwords.items():
        hash_value = generate_password_hash(password)
        print(f"\nПользователь: {username}")
        print(f"Пароль: {password}")
        print(f"Хеш: {hash_value}")
    
    # Интерактивный режим
    print("\n" + "="*50)
    print("Создать новый пароль? (Enter для выхода)")
    
    while True:
        password = input("\nВведите пароль: ").strip()
        if not password:
            break
        
        hash_value = generate_password_hash(password)
        print(f"Хеш: {hash_value}")
        print("\nДобавьте в USERS_DB в app/auth.py:")
        print(f'"username": {{')
        print(f'    "username": "username",')
        print(f'    "hashed_password": "{hash_value}",')
        print(f'    "role": "user"')
        print(f'}}')
