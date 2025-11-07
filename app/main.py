from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from app.predictor import CreditScoringPredictor
from app.auth import (
    get_current_user, get_current_admin_user, authenticate_user,
    create_access_token, Token, LoginRequest, User, ACCESS_TOKEN_EXPIRE_MINUTES
)
import logging
import pandas as pd
from datetime import datetime, timedelta
from fastapi import Body

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Credit Scoring API",
    description="AI-based credit scoring system for small retailers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor
try:
    predictor = CreditScoringPredictor(models_dir='models')
    logger.info("✅ Models loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load models: {e}")
    raise


# ========================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE
# ========================================================================

class ClientData(BaseModel):
    """Client financial data for prediction"""
    data: Dict[str, float] = Field(..., description="Client features as key-value pairs")

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "INCOME": 180000,
                    "SAVINGS": 450000,
                    "DEBT": 320000,
                    "R_DEBT_INCOME": 1.78
                }
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response model"""
    default_probability: float
    default_class: int
    risk_level: str
    decision: str
    credit_score: float
    score_range: str


class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    clients: List[Dict[str, float]]


class ModelInfo(BaseModel):
    """Model metadata"""
    created_at: str
    models: dict
    features: List[str]
    n_features: int
    dataset_info: Optional[dict] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str


# ========================================================================
# ENDPOINTS
# ========================================================================

@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login(login_data: LoginRequest):
    """
    Авторизация пользователя
    
    **Тестовые учетные данные:**
    - admin / secret (полный доступ)
    - user / password (ограниченный доступ)
    """
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверное имя пользователя или пароль"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User {user['username']} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", tags=["Authentication"])
async def get_me(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return {
        "username": current_user.username,
        "role": current_user.role
    }


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Credit Scoring API",
        "status": "running",
        "version": "1.0.0",
        "authentication": {
            "login": "/auth/login",
            "me": "/auth/me"
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "predict": "/predict",
            "batch": "/predict/batch",
            "model_info": "/model-info",
            "features": "/features"
        }
    }

TOP_FEATURES = [
    "R_DEBT_INCOME", "DEBT", "INCOME", "R_EXPENDITURE",
    "SAVINGS", "R_SAVINGS_INCOME", "R_GROCERIES", "R_HOUSING",
    "T_EXPENDITURE_12", "R_GAMBLING", "T_HOUSING_12", "T_GROCERIES_12"
]

@app.post("/predict_slim", tags=["Prediction"])
async def predict_slim(user_data: dict = Body(...), current_user: User = Depends(get_current_user)):
    """
    Принимает только 12 топ-признаков, остальные подставляет средними.
    
    **Требуется авторизация**
    """
    # Подгрузи средние значения всех признаков (feature_means загружаются при старте, как в прошлой инструкции)
    feature_means_only = {k: v for k, v in predictor.feature_means.items() if k in predictor.metadata['features']}
    features = feature_means_only.copy()
    # Обновляем только значимые
    for key in TOP_FEATURES:
        if key in user_data:
            features[key] = user_data[key]
    print("Собираем такой вектор:", features)
    result = predictor.predict_full(features)
    logger.info(f"Slim prediction by {current_user.username}")
    return result

@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/model-info", response_model=ModelInfo, tags=["Model Information"])
async def get_model_info(current_user: User = Depends(get_current_admin_user)):
    """
    Get detailed model metadata and performance metrics
    
    **Требуется роль администратора**

    Returns information about:
    - Model training date
    - Performance metrics (ROC-AUC, R², etc.)
    - Feature list
    - Dataset statistics
    """
    try:
        return predictor.get_model_info()
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/features", tags=["Model Information"])
async def get_features():
    """
    Get list of all required features for prediction

    Returns the complete list of 84 features needed for prediction
    """
    try:
        metadata = predictor.get_model_info()
        return {
            "features": metadata['features'],
            "count": metadata['n_features'],
            "example_values": {
                "INCOME": 180000,
                "SAVINGS": 450000,
                "DEBT": 320000,
                "R_DEBT_INCOME": 1.78
            }
        }
    except Exception as e:
        logger.error(f"Error getting features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(client_data: ClientData, current_user: User = Depends(get_current_user)):
    """
    Predict credit risk and score for a single client
    
    **Требуется авторизация**

    **Required**: All 84 features must be provided in the request

    **Returns**:
    - Credit score (300-800 range)
    - Default probability (0-100%)
    - Risk level (Low/Medium/High)
    - Decision (APPROVE/REVIEW/REJECT)
    """
    try:
        # Make prediction
        result = predictor.predict_full(client_data.data)

        logger.info(f"Prediction made by {current_user.username}: {result['decision']} (Score: {result['credit_score']:.2f})")
        return result

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/default", tags=["Prediction"])
async def predict_default_only(client_data: ClientData, current_user: User = Depends(get_current_user)):
    """
    Predict only default probability (faster than full prediction)
    
    **Требуется авторизация**

    Returns default probability and risk classification
    """
    try:
        result = predictor.predict_default(client_data.data)
        logger.info(f"Default prediction by {current_user.username}: {result['default_probability']:.2f}%")
        return result
    except Exception as e:
        logger.error(f"Default prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/score", tags=["Prediction"])
async def predict_score_only(client_data: ClientData, current_user: User = Depends(get_current_user)):
    """
    Predict only credit score (faster than full prediction)
    
    **Требуется авторизация**

    Returns credit score prediction
    """
    try:
        result = predictor.predict_credit_score(client_data.data)
        logger.info(f"Score prediction by {current_user.username}: {result['credit_score']:.2f}")
        return result
    except Exception as e:
        logger.error(f"Score prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(request: BatchPredictionRequest, current_user: User = Depends(get_current_user)):
    """
    Predict credit risk for multiple clients at once
    
    **Требуется авторизация**

    **Input**: Array of client data objects
    **Returns**: Array of predictions

    Useful for processing multiple loan applications simultaneously
    """
    try:
        results = []
        for i, client_data in enumerate(request.clients):
            try:
                result = predictor.predict_full(client_data)
                result['client_index'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing client {i}: {e}")
                results.append({
                    'client_index': i,
                    'error': str(e)
                })

        logger.info(f"Batch prediction by {current_user.username} completed: {len(results)} clients")
        return {
            "total": len(request.clients),
            "successful": len([r for r in results if 'error' not in r]),
            "predictions": results
        }

    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics", tags=["Analytics"])
async def get_statistics():
    """
    Get model statistics and thresholds

    Returns decision thresholds and risk level definitions
    """
    return {
        "risk_thresholds": {
            "low": {
                "max_default_probability": 30,
                "decision": "APPROVE",
                "description": "Low risk - Recommended for approval"
            },
            "medium": {
                "min_default_probability": 30,
                "max_default_probability": 50,
                "decision": "REVIEW",
                "description": "Medium risk - Requires review"
            },
            "high": {
                "min_default_probability": 50,
                "decision": "REJECT",
                "description": "High risk - Not recommended"
            }
        },
        "score_range": {
            "min": 300,
            "max": 800,
            "description": "Credit score range"
        },
        "model_performance": predictor.metadata.get('models', {})
    }


# ========================================================================
# ERROR HANDLERS
# ========================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "path": str(request.url),
        "available_endpoints": [
            "/docs",
            "/health",
            "/predict",
            "/predict/batch",
            "/model-info"
        ]
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal server error",
        "message": str(exc)
    }


# ========================================================================
# STARTUP/SHUTDOWN EVENTS
# ========================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Credit Scoring API started")
    logger.info(f"📊 Model features: {predictor.metadata['n_features']}")
    logger.info("📖 Documentation: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Credit Scoring API shutting down")


# ========================================================================
# RUN SERVER
# ========================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
