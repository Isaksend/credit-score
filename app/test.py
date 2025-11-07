import requests
import json

# ========================================================================
# COMPLETE TEST WITH ALL 84 FEATURES
# ========================================================================

client_data = {
    "data": {
        # Financial basics
        "INCOME": 180000,
        "SAVINGS": 450000,
        "DEBT": 320000,

        # Savings and debt ratios
        "R_SAVINGS_INCOME": 2.5,
        "R_DEBT_INCOME": 1.78,
        "R_DEBT_SAVINGS": 0.71,

        # Clothing expenses
        "T_CLOTHING_12": 48000,
        "T_CLOTHING_6": 24000,
        "R_CLOTHING": 0.027,
        "R_CLOTHING_INCOME": 0.027,
        "R_CLOTHING_SAVINGS": 0.011,
        "R_CLOTHING_DEBT": 0.015,

        # Education expenses
        "T_EDUCATION_12": 72000,
        "T_EDUCATION_6": 36000,
        "R_EDUCATION": 0.040,
        "R_EDUCATION_INCOME": 0.040,
        "R_EDUCATION_SAVINGS": 0.016,
        "R_EDUCATION_DEBT": 0.023,

        # Entertainment expenses
        "T_ENTERTAINMENT_12": 96000,
        "T_ENTERTAINMENT_6": 48000,
        "R_ENTERTAINMENT": 0.053,
        "R_ENTERTAINMENT_INCOME": 0.053,
        "R_ENTERTAINMENT_SAVINGS": 0.021,
        "R_ENTERTAINMENT_DEBT": 0.030,

        # Fines
        "T_FINES_12": 12000,
        "T_FINES_6": 6000,
        "R_FINES": 0.007,
        "R_FINES_INCOME": 0.007,
        "R_FINES_SAVINGS": 0.003,
        "R_FINES_DEBT": 0.004,

        # Gambling expenses
        "T_GAMBLING_12": 18000,
        "T_GAMBLING_6": 9000,
        "R_GAMBLING": 0.010,
        "R_GAMBLING_INCOME": 0.010,
        "R_GAMBLING_SAVINGS": 0.004,
        "R_GAMBLING_DEBT": 0.006,

        # Groceries expenses
        "T_GROCERIES_12": 240000,
        "T_GROCERIES_6": 120000,
        "R_GROCERIES": 0.133,
        "R_GROCERIES_INCOME": 0.133,
        "R_GROCERIES_SAVINGS": 0.053,
        "R_GROCERIES_DEBT": 0.075,

        # Health expenses
        "T_HEALTH_12": 84000,
        "T_HEALTH_6": 42000,
        "R_HEALTH": 0.047,
        "R_HEALTH_INCOME": 0.047,
        "R_HEALTH_SAVINGS": 0.019,
        "R_HEALTH_DEBT": 0.026,

        # Housing expenses
        "T_HOUSING_12": 360000,
        "T_HOUSING_6": 180000,
        "R_HOUSING": 0.200,
        "R_HOUSING_INCOME": 0.200,
        "R_HOUSING_SAVINGS": 0.080,
        "R_HOUSING_DEBT": 0.113,

        # Tax payments
        "T_TAX_12": 216000,
        "T_TAX_6": 108000,
        "R_TAX": 0.120,
        "R_TAX_INCOME": 0.120,
        "R_TAX_SAVINGS": 0.048,
        "R_TAX_DEBT": 0.068,

        # Travel expenses
        "T_TRAVEL_12": 144000,
        "T_TRAVEL_6": 72000,
        "R_TRAVEL": 0.080,
        "R_TRAVEL_INCOME": 0.080,
        "R_TRAVEL_SAVINGS": 0.032,
        "R_TRAVEL_DEBT": 0.045,

        # Utilities expenses
        "T_UTILITIES_12": 120000,
        "T_UTILITIES_6": 60000,
        "R_UTILITIES": 0.067,
        "R_UTILITIES_INCOME": 0.067,
        "R_UTILITIES_SAVINGS": 0.027,
        "R_UTILITIES_DEBT": 0.038,

        # Total expenditure
        "T_EXPENDITURE_12": 1410000,
        "T_EXPENDITURE_6": 705000,
        "R_EXPENDITURE": 0.783,
        "R_EXPENDITURE_INCOME": 0.783,
        "R_EXPENDITURE_SAVINGS": 0.313,
        "R_EXPENDITURE_DEBT": 0.441,

        # Categorical features (binary: 0 or 1)
        "CAT_DEBT": 1,
        "CAT_CREDIT_CARD": 1,
        "CAT_MORTGAGE": 1,
        "CAT_SAVINGS_ACCOUNT": 1,
        "CAT_DEPENDENTS": 0,

        # Encoded categorical (from LabelEncoder)
        "CAT_GAMBLING_ENCODED": 2
    }
}

# ========================================================================
# SEND REQUEST TO API
# ========================================================================

url = "http://localhost:8000/predict"

print("=" * 80)
print("TESTING CREDIT SCORING API")
print("=" * 80)
print(f"\nAPI URL: {url}")
print(f"Number of features sent: {len(client_data['data'])}")
print(f"\nClient Profile:")
print(f"  Income: ${client_data['data']['INCOME']:,}")
print(f"  Savings: ${client_data['data']['SAVINGS']:,}")
print(f"  Debt: ${client_data['data']['DEBT']:,}")
print(f"  Debt-to-Income Ratio: {client_data['data']['R_DEBT_INCOME']:.2f}")

try:
    print("\n" + "-" * 80)
    print("Sending request...")

    response = requests.post(url, json=client_data, timeout=10)

    if response.status_code == 200:
        result = response.json()

        print("\n" + "=" * 80)
        print("✅ PREDICTION SUCCESSFUL")
        print("=" * 80)
        print(f"\n📊 Credit Score:          {result['credit_score']:.2f} / 800")
        print(f"⚠️  Default Probability:   {result['default_probability']:.2f}%")
        print(f"📈 Risk Level:            {result['risk_level']}")
        print(f"🎯 Decision:              {result['decision']}")
        print(f"📅 Score Range:           {result['score_range']}")
        print("=" * 80)

        # Interpretation
        print("\n💡 INTERPRETATION:")
        if result['decision'] == "APPROVE":
            print("   ✅ Low risk client - Recommended for loan approval")
        elif result['decision'] == "REVIEW":
            print("   ⚠️  Medium risk - Requires additional review")
        else:
            print("   ❌ High risk - Not recommended for loan approval")

        # Save result
        with open('prediction_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\n📄 Result saved to: prediction_result.json")

    else:
        print(f"\n❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR!")
    print("Make sure the API server is running:")
    print("   uvicorn app.main:app --reload")

except requests.exceptions.Timeout:
    print("\n❌ REQUEST TIMEOUT!")
    print("Server took too long to respond")

except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {e}")

print("\n" + "=" * 80)
