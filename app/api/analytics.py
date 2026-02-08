# app/api/analytics.py
import os
import pandas as pd
from fastapi import APIRouter

router = APIRouter()

# ---------------------------
# BASE DIR (backened/)
# ---------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------
# CSV PATHS
# ---------------------------
TEACHERS_CSV = os.path.join(BASE_DIR, "data", "teachers.csv")
COURSES_CSV = os.path.join(BASE_DIR, "data", "courses.csv")
TRANSACTIONS_CSV = os.path.join(BASE_DIR, "data", "transactions.csv")

# ---------------------------
# LOAD CSVs ONCE
# ---------------------------
teachers_df = pd.read_csv(TEACHERS_CSV)
courses_df = pd.read_csv(COURSES_CSV)
transactions_df = pd.read_csv(TRANSACTIONS_CSV)

# ---------------------------
# MERGE DATA (for analytics)
# ---------------------------
merged_df = transactions_df.merge(teachers_df, on="TeacherID", how="left")
merged_df = merged_df.merge(courses_df, on="CourseID", how="left")

# ---------------------------
# KPI ENDPOINT
# ---------------------------
@router.get("/")
def get_kpis():
    return {
        "total_instructors": int(teachers_df["TeacherID"].nunique()),
        "total_courses": int(courses_df["CourseID"].nunique()),
        "total_transactions": int(transactions_df["TransactionID"].nunique()),
        "avg_teacher_rating": round(float(teachers_df["TeacherRating"].mean()), 2),
        "avg_course_rating": round(float(courses_df["CourseRating"].mean()), 2),
    }
@router.get("/top-instructors")
def top_instructors(limit: int = 10):

    leaderboard = teachers_df.sort_values(
        by="TeacherRating", ascending=False
    ).head(limit)

    return leaderboard.to_dict(orient="records")
@router.get("/teacher-vs-course-rating")
def teacher_vs_course_rating():

    df = merged_df[["TeacherRating", "CourseRating"]].dropna()

    corr = df["TeacherRating"].corr(df["CourseRating"])

    return {
        "correlation": round(float(corr), 3),
        "data_points": df.to_dict(orient="records")
    }
@router.get("/enrollments-by-rating-tier")
def enrollments_by_rating_tier():

    df = merged_df[["TeacherID", "TeacherRating", "TransactionID"]].dropna()

    # Create rating tiers
    def tier(r):
        if r >= 4.5:
            return "High Rated (>=4.5)"
        elif r >= 3.5:
            return "Mid Rated (3.5 - 4.49)"
        else:
            return "Low Rated (<3.5)"

    df["RatingTier"] = df["TeacherRating"].apply(tier)

    result = df.groupby("RatingTier")["TransactionID"].count().reset_index()
    result = result.rename(columns={"TransactionID": "TotalEnrollments"})

    return result.to_dict(orient="records")
@router.get("/expertise-performance")

def expertise_performance():

    df = merged_df[["Expertise", "TeacherRating", "CourseRating", "CourseID"]].dropna()

    result = (
        df.groupby("Expertise")
        .agg(
            avg_teacher_rating=("TeacherRating", "mean"),
            avg_course_rating=("CourseRating", "mean"),
            total_courses=("CourseID", "nunique"),
            total_enrollments=("CourseID", "count")
        )
        .reset_index()
    )

    result["avg_teacher_rating"] = result["avg_teacher_rating"].round(2)
    result["avg_course_rating"] = result["avg_course_rating"].round(2)

    result = result.sort_values(by="avg_course_rating", ascending=False)

    return result.to_dict(orient="records")
@router.get("/rating-consistency")
def rating_consistency():

    df = merged_df[["TeacherID", "TeacherName", "CourseRating"]].dropna()

    result = (
        df.groupby(["TeacherID", "TeacherName"])
        .agg(
            avg_course_rating=("CourseRating", "mean"),
            rating_std=("CourseRating", "std"),
            total_courses=("CourseRating", "count"),
        )
        .reset_index()
    )

    # Fill NaN std (happens when only 1 course) with 0
    result["rating_std"] = result["rating_std"].fillna(0)

    # Consistency Score (higher = better)
    # small std = more consistent, so we invert it
    result["consistency_score"] = 1 / (1 + result["rating_std"])

    # Round values
    result["avg_course_rating"] = result["avg_course_rating"].round(2)
    result["rating_std"] = result["rating_std"].round(2)
    result["consistency_score"] = result["consistency_score"].round(3)

    # Sort: best consistency first
    result = result.sort_values(by="consistency_score", ascending=False)

    return result.to_dict(orient="records")





