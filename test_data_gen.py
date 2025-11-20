import requests
import random
import json
from copy import deepcopy

# === 1. Загрузка средних значений признаков (feature_means.json) ===
FEATURE_MEANS_FILE = "models/feature_means.json"

with open(FEATURE_MEANS_FILE, "r") as f:
    feature_means = json.load(f)

all_features = feature_means["features"]
mean_values = {k: feature_means[k] for k in all_features}

# === 2. Ключевые признаки для вариаций (TOP 12 + категориальные) ===
TOP_FEATURES = [
    "R_DEBT_INCOME", "DEBT", "INCOME", "R_EXPENDITURE",
    "SAVINGS", "R_SAVINGS_INCOME", "R_GROCERIES", "R_HOUSING",
    "T_EXPENDITURE_12", "R_GAMBLING", "T_HOUSING_12", "T_GROCERIES_12"
]
CATEGORICALS = [
    "CAT_DEBT", "CAT_CREDIT_CARD", "CAT_MORTGAGE",
    "CAT_SAVINGS_ACCOUNT", "CAT_DEPENDENTS", "CAT_GAMBLING_ENCODED"
]

# === 3. Функция генерации клиента ===
def generate_client(seed=None):
    # Базовые значения — средние
    client = deepcopy(mean_values)
    # Варьируем ключевые
    client["INCOME"] = random.randint(60000, 250000)
    client["DEBT"] = random.randint(0, int(client["INCOME"] * random.uniform(0.5, 8)))
    client["SAVINGS"] = random.randint(0, int(client["INCOME"] * random.uniform(0.7, 6)))
    client["R_DEBT_INCOME"] = round(client["DEBT"] / (client["INCOME"] + 1), 3)
    client["R_EXPENDITURE"] = round(random.uniform(0.3, 0.8), 3)
    client["R_SAVINGS_INCOME"] = round(client["SAVINGS"] / (client["INCOME"] + 1), 3)
    client["R_GROCERIES"] = round(random.uniform(0.1, 0.8), 3)
    client["R_HOUSING"] = round(random.uniform(0.05, 0.8), 3)
    client["T_EXPENDITURE_12"] = random.randint(5000, client["INCOME"])
    client["T_GROCERIES_12"] = random.randint(1000, client["T_EXPENDITURE_12"])
    client["R_GAMBLING"] = round(random.uniform(0, 0.8), 3)
    client["T_HOUSING_12"] = random.randint(0, 0 if client["INCOME"] < 70000 else int(client["INCOME"] * 0.3))

    # Категориальные (0, 1, 2), для CAT_GAMBLING_ENCODED — 0/1/2, остальные — 0 или 1
    client["CAT_DEBT"] = random.choice([0, 1])
    client["CAT_CREDIT_CARD"] = random.choice([0, 1])
    client["CAT_MORTGAGE"] = random.choice([0, 1])
    client["CAT_SAVINGS_ACCOUNT"] = random.choice([0, 1])
    client["CAT_DEPENDENTS"] = random.choice([0, 1, 2])
    client["CAT_GAMBLING_ENCODED"] = random.choice([0, 1, 2])

    # Можно варьировать любые другие признаки при необходимости — для богатства данных
    return client

# === 4. Генерируем и отправляем пачку клиентов ===
def main():
    BATCH_SIZE = 30
    clients = [generate_client() for _ in range(BATCH_SIZE)]

    url = "http://localhost:8000/predict/batch"  # твой backend (локально)
    payload = {"clients": clients}

    print(f"Отправляем {BATCH_SIZE} клиентов...")
    response = requests.post(url, json=payload)
    if response.ok:
        res = response.json()
        print("Batch scoring успешно завершён!")
        print(f"Всего обработано: {res['total']}, успешных: {res['successful']}")
        # Выведем первые 3 результата:
        for client in res['predictions'][:3]:
            print("\nКлиент:", client)
    else:
        print("Ошибка при запросе:", response.status_code, response.text)

if __name__ == "__main__":
    main()