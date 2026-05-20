from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes.auth_routes import router as auth_router
from app.routes.analytics_routes import router as analytics_router
from app.routes.billing_routes import router as billing_router
from app.routes.career_tools_routes import router as career_tools_router
from app.routes.job_routes import router as job_router
from app.routes.scan_routes import router as scan_router
from app.routes.support_routes import router as support_router

from app.models import user, job_description, scan, score_result, suggestion, job_application


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ResumeRank API",
    description="Job Resume Match Scorer API using FastAPI and pure Python NLP",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later we will replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "ResumeRank API is running successfully"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.include_router(auth_router)
app.include_router(analytics_router)
app.include_router(billing_router)
app.include_router(career_tools_router)
app.include_router(job_router)
app.include_router(scan_router)
app.include_router(support_router)
