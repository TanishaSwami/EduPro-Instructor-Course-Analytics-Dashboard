from fastapi import FastAPI
from app.api import instructors
from app.api import analytics
app=FastAPI(title="EduPro Backend")
app.include_router(instructors.router,prefix="/instructors")
app.include_router(analytics.router, prefix="/analytics")
@app.get("/")
def home():
    return {"message": "Welcome to EduPro Backend!"}