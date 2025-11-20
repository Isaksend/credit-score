from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
import json
import os

from app.api.predict import router as predict_router  # Импортируй router

app = FastAPI(
    title="Credit Scoring API",
    description="AI-based credit scoring system for small retailers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(predict_router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
PORTFOLIO_HISTORY_FILE = "portfolio_history.json"

@app.get("/", tags=["General"])
async def root():
    return {
        "message": "Credit Scoring API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/docs", "/health", "/predict", "/portfolio/clients",
            "/portfolio/statistics", "/statistics"
        ]
    }

@app.get("/health", tags=["General"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/portfolio/clients", tags=["Portfolio"])
async def get_portfolio_clients():
    try:
        if os.path.exists(PORTFOLIO_HISTORY_FILE):
            with open(PORTFOLIO_HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []
        return {"clients": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Error fetching portfolio history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/statistics", tags=["Portfolio"])
async def get_portfolio_statistics():
    try:
        if not os.path.exists(PORTFOLIO_HISTORY_FILE):
            return {"count": 0, "msg": "No portfolio data"}
        with open(PORTFOLIO_HISTORY_FILE, "r") as f:
            history = json.load(f)
        scores, probs = [], []
        risks = {"Low": 0, "Medium": 0, "High": 0}
        decisions = {"APPROVE": 0, "REVIEW": 0, "REJECT": 0}
        score_hist = [0]*6
        prob_hist = [0]*5
        for entry in history:
            res = entry.get("result", {})
            score = res.get("credit_score")
            prob = res.get("default_probability")
            risk = res.get("risk_level")
            decision = res.get("decision")
            if isinstance(score, (int, float)):
                bin_id = min(5, max(0, int((score - 300)//100)))
                score_hist[bin_id] += 1
                scores.append(score)
            if isinstance(prob, (int, float)):
                bin_id = min(4, max(0, int(prob//20)))
                prob_hist[bin_id] += 1
                probs.append(prob)
            if risk in risks: risks[risk] += 1
            if decision in decisions: decisions[decision] += 1
        n = len(history)
        avg_score = round(sum(scores)/n,2) if n else None
        avg_prob = round(sum(probs)/n,2) if n else None
        return {
            "count": n,
            "avg_score": avg_score,
            "avg_default_probability": avg_prob,
            "risk_distribution": {k: round(v/n*100,2) if n else 0 for k, v in risks.items()},
            "decision_distribution": {k: round(v/n*100,2) if n else 0 for k, v in decisions.items()},
            "score_histogram": {
                "bins": ["300-400","400-500","500-600","600-700","700-800","800+"],
                "counts": score_hist
            },
            "default_probability_histogram": {
                "bins": ["0-20","20-40","40-60","60-80","80-100"],
                "counts": prob_hist
            }
        }
    except Exception as e:
        logger.error(f"Error computing portfolio statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics", tags=["Analytics"])
async def get_statistics():
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
    }

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Credit Scoring API started")
    logger.info("📖 Documentation: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Credit Scoring API shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
