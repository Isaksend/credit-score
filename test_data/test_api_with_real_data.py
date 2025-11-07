import requests
import json

# Load test examples
with open('all_test_examples.json', 'r') as f:
    examples = json.load(f)

# API endpoint
url = "http://localhost:8000/predict"

print("="*80)
print("TESTING CREDIT SCORING API WITH REAL DATA")
print("="*80)

for example in examples:
    print(f"\n{'='*80}")
    print(f"Testing: {example['client_id']}")
    print(f"Description: {example['description']}")
    print(f"Actual Credit Score: {example['actual_credit_score']:.2f}")
    print(f"Actual Default: {'Yes' if example['actual_default'] == 1 else 'No'}")
    print("-"*80)
    
    # Prepare request
    client_data = {"data": example['features']}
    
    try:
        # Send request
        response = requests.post(url, json=client_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n📊 Predicted Credit Score:    {result['credit_score']:.2f}")
            print(f"⚠️  Default Probability:       {result['default_probability']:.2f}%")
            print(f"📈 Risk Level:                {result['risk_level']}")
            print(f"🎯 Decision:                  {result['decision']}")
            
            # Compare with actual
            score_diff = abs(result['credit_score'] - example['actual_credit_score'])
            print(f"\n📉 Score Difference:          {score_diff:.2f} points")
            
            if score_diff < 50:
                print("   ✅ Good prediction accuracy!")
            elif score_diff < 100:
                print("   ⚠️  Moderate prediction accuracy")
            else:
                print("   ❌ Large prediction error")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n{'='*80}")
print("TESTING COMPLETED")
print("="*80)
