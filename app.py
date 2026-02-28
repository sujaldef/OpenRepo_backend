from fastapi import FastAPI
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware

# -----------------------
# FASTAPI APP FIRST
# -----------------------
app = FastAPI(title="Code Audit Backend")

# -----------------------
# CORS AFTER APP CREATED
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# DATABASE
# -----------------------
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["code_audit"]

users = db.users
repos = db.repos
files = db.files
error_reports = db.error_reports
prediction_reports = db.prediction_reports
recommendation_reports = db.recommendation_reports
summaries = db.summaries

# -----------------------
# ROUTERS
# -----------------------
from controllers.auth_controller import router as auth_router
from controllers.repo_controller import router as repo_router

from controllers.error_controller import router as error_router
from controllers.prediction_controller import router as prediction_router
from controllers.recommendation_controller import router as recommendation_router
from controllers.summary_controller import router as summary_router

app.include_router(auth_router)
app.include_router(repo_router)

app.include_router(error_router)
app.include_router(prediction_router)
app.include_router(recommendation_router)
app.include_router(summary_router)

# -----------------------
# ROOT
# -----------------------
@app.get("/")
def root():
    return {"status": "Backend running 🚀"}
