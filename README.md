🚦 Credit Score Backend
Credit Score Backend powers the scoring, risk assessment, and client management APIs for your digital credit scoring platform.
Built with fast, secure Python technologies (FastAPI, scikit-learn), ready for real-time integration and analytics.

✨ Features
- Predict Credit Score — POST endpoint for instant credit scoring and risk probability output.

- User Authentication — Secure JWT-based signup / login / user management.

- Flexible Model Integration — Plug your trained ML models (scikit-learn, pickle, etc).

- Feature Selection & Engineering — Select features, blend with means, auto-calculate ratios.

- Modular API Design — Easy to extend, integrate, and document endpoints.

- Error Handling — Robust validation and clean developer responses.

🛠️ Tech Stack
Python 3.12+

FastAPI — Fast web server & REST API

scikit-learn — Model loading/prediction

Uvicorn — ASGI high-performance server

PyJWT / passlib — Auth & password hashing

pydantic — Data validation

StandardScaler — Feature scaling

⚡ Quick Start
git clone https://github.com/Isaksend/credit-score-backend.git
cd credit-score-backend
python3 -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
# Place model and feature files into the /models directory (see below)
uvicorn main:app --reload
# Open http://localhost:8000/docs for interactive API
📁 File Structure
models/
  linear_model.pkl
  logistic_model.pkl
  scaler.pkl
  feature_means.json
src/
  main.py
  routers/
    predict.py
    auth.py
  schemas/
    client.py
    user.py
requirements.txt
README.md

🔗 API Endpoints
| Method | Route        | Description            |
| ------ | ------------ | ---------------------- |
| POST   | /predict     | Predict score + risk   |
| POST   | /auth/signup | Register user          |
| POST   | /auth/login  | Authenticate & get JWT |
/predict:
Expects client feature data as JSON. Returns predicted score, risk probability, risk level, and decision.

/auth:
Simple JWT-based authentication for your web/frontend integration.

🧑‍🔧 Usage Notes
Feature Engineering:
Features must be named and ordered just as in your model training pipeline (see features_for_model).

Model Files:
Place linear_model.pkl, logistic_model.pkl, scaler.pkl, and feature_means.json in /models.

Custom Feature Calculation:
Backend auto-merges user data with mean values, computes derived features if needed.

Error Handling:
Returns informative error messages for missing/invalid parameters.

🔒 Security
Passwords are hashed with passlib (bcrypt).

JWT tokens are used for protected endpoints.

🚀 Extending
Add endpoints for history, audit, batch processing, admin, analytics.

Plug other models or feature selectors.

Integrate with any SQL/NoSQL storage.

📝 License
MIT

For support or contributions:
Open issues, send PRs, or contact the repository owner!

