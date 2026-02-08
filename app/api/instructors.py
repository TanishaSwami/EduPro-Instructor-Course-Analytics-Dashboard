# app/api/instructors.py
import os
import pandas as pd
from fastapi import APIRouter

router = APIRouter()

# Get the project root (3 levels up from this file)
# file is app/api/instructors.py -> go up to backened/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CSV file paths
TEACHERS_CSV = os.path.join(BASE_DIR, "data", "teachers.csv")
COURSES_CSV = os.path.join(BASE_DIR, "data", "courses.csv")
TRANSACTIONS_CSV = os.path.join(BASE_DIR, "data", "transactions.csv")

# Load CSVs once
teachers_df = pd.read_csv(TEACHERS_CSV)
courses_df = pd.read_csv(COURSES_CSV)
transactions_df = pd.read_csv(TRANSACTIONS_CSV)

# Simple test endpoint
@router.get("/")
def get_instructors():
    return teachers_df.to_dict(orient="records")
