# src/api/predict.py
from fastapi import APIRouter
from pydantic import BaseModel
import numpy as np
import pandas as pd
import joblib
import json

with open('models/feature_means.json') as f:
    feature_means = json.load(f)
scaler = joblib.load('models/scaler.joblib')
encoder = joblib.load('models/label_encoder.joblib')

# Модели
linear_model = joblib.load("models/linear_regression.joblib")
logistic_model = joblib.load("models/logistic_model.joblib")

router = APIRouter()

features_for_model = [
        "INCOME",
        "SAVINGS",
        "DEBT",
        "R_SAVINGS_INCOME",
        "R_DEBT_INCOME",
        "R_DEBT_SAVINGS",
        "T_CLOTHING_12",
        "T_CLOTHING_6",
        "R_CLOTHING",
        "R_CLOTHING_INCOME",
        "R_CLOTHING_SAVINGS",
        "R_CLOTHING_DEBT",
        "T_EDUCATION_12",
        "T_EDUCATION_6",
        "R_EDUCATION",
        "R_EDUCATION_INCOME",
        "R_EDUCATION_SAVINGS",
        "R_EDUCATION_DEBT",
        "T_ENTERTAINMENT_12",
        "T_ENTERTAINMENT_6",
        "R_ENTERTAINMENT",
        "R_ENTERTAINMENT_INCOME",
        "R_ENTERTAINMENT_SAVINGS",
        "R_ENTERTAINMENT_DEBT",
        "T_FINES_12",
        "T_FINES_6",
        "R_FINES",
        "R_FINES_INCOME",
        "R_FINES_SAVINGS",
        "R_FINES_DEBT",
        "T_GAMBLING_12",
        "T_GAMBLING_6",
        "R_GAMBLING",
        "R_GAMBLING_INCOME",
        "R_GAMBLING_SAVINGS",
        "R_GAMBLING_DEBT",
        "T_GROCERIES_12",
        "T_GROCERIES_6",
        "R_GROCERIES",
        "R_GROCERIES_INCOME",
        "R_GROCERIES_SAVINGS",
        "R_GROCERIES_DEBT",
        "T_HEALTH_12",
        "T_HEALTH_6",
        "R_HEALTH",
        "R_HEALTH_INCOME",
        "R_HEALTH_SAVINGS",
        "R_HEALTH_DEBT",
        "T_HOUSING_12",
        "T_HOUSING_6",
        "R_HOUSING",
        "R_HOUSING_INCOME",
        "R_HOUSING_SAVINGS",
        "R_HOUSING_DEBT",
        "T_TAX_12",
        "T_TAX_6",
        "R_TAX",
        "R_TAX_INCOME",
        "R_TAX_SAVINGS",
        "R_TAX_DEBT",
        "T_TRAVEL_12",
        "T_TRAVEL_6",
        "R_TRAVEL",
        "R_TRAVEL_INCOME",
        "R_TRAVEL_SAVINGS",
        "R_TRAVEL_DEBT",
        "T_UTILITIES_12",
        "T_UTILITIES_6",
        "R_UTILITIES",
        "R_UTILITIES_INCOME",
        "R_UTILITIES_SAVINGS",
        "R_UTILITIES_DEBT",
        "T_EXPENDITURE_12",
        "T_EXPENDITURE_6",
        "R_EXPENDITURE",
        "R_EXPENDITURE_INCOME",
        "R_EXPENDITURE_SAVINGS",
        "R_EXPENDITURE_DEBT",
        "CAT_DEBT",
        "CAT_CREDIT_CARD",
        "CAT_MORTGAGE",
        "CAT_SAVINGS_ACCOUNT",
        "CAT_DEPENDENTS",
        "CAT_GAMBLING_ENCODED"
]


class ClientData(BaseModel):
    income: float
    debt: float
    expenditure: float
    savings: float
    credit_card: int
    mortgage: int
    dependents: int

def preprocess_features(data: ClientData):
    r_debt_income = data.debt / data.income if data.income else 0
    r_savings_income = data.savings / data.income if data.income else 0
    r_expenditure_income = data.expenditure / data.income if data.income else 0

    features = [
        data.income,
        data.debt,
        data.expenditure,
        data.savings,
        data.credit_card,
        data.mortgage,
        data.dependents,
        r_debt_income,
        r_savings_income,
        r_expenditure_income,
    ]
    return np.array(features).reshape(1, -1)

def make_full_vector(input_dict):
    # Приводим ключи к верхнему регистру
    input_dict_upper = {k.upper(): v for k, v in input_dict.items()}
    features = feature_means.copy()
    features.update(input_dict_upper)
    ordered = [features[k] for k in features_for_model]
    print("Features for predict (ordered):", ordered)  # DEBUG
    arr = np.array(ordered).reshape(1, -1)
    arr_scaled = scaler.transform(arr)
    return arr_scaled


@router.post("/predict")
async def predict_score(client: ClientData):
    features = make_full_vector(client.dict())
    credit_score = float(linear_model.predict(features)[0])
    default_prob = float(logistic_model.predict_proba(features)[0][1])

    print("credit_score:", credit_score)
    print("default_prob:", default_prob)

    if default_prob > 0.8:
        decision = "REJECT"
        risk_level = "High"
    elif default_prob > 0.5:
        decision = "REVIEW"
        risk_level = "Medium"
    else:
        decision = "APPROVE"
        risk_level = "Low"
    return {
        "result": {
            "credit_score": round(credit_score, 2),
            "default_probability": round(default_prob * 100, 2),
            "risk_level": risk_level,
            "decision": decision
        }
    }
    print("Features for predict (after update):", features)


