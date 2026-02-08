import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="EduPro Dashboard", layout="wide")

st.title("📊 EduPro Instructor & Course Analytics Dashboard")

st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Overview", "Top Instructors", "Rating Analysis", "Enrollments", "Expertise Insights", "Consistency"],
)




# -----------------------------
# Helper function to fetch API
# -----------------------------
def fetch_data(endpoint):
    url = f"{BASE_URL}/analytics{endpoint}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"API Error {res.status_code} for {url}")
            return None
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return None


# ==========================================================
# 1) KPI SECTION  (Your KPI endpoint is "/analytics/")
# ==========================================================
if page=="Overview":
   st.subheader("📌 Platform KPIs")

   kpis = fetch_data("/")   # because your KPI endpoint is @router.get("/")

   if kpis:
       c1, c2, c3, c4, c5 = st.columns(5)

       c1.metric("Total Instructors", kpis["total_instructors"])
       c2.metric("Total Courses", kpis["total_courses"])
       c3.metric("Total Enrollments", kpis["total_transactions"])
       c4.metric("Avg Teacher Rating", kpis["avg_teacher_rating"])
       c5.metric("Avg Course Rating", kpis["avg_course_rating"])


# ==========================================================
# 2) TOP INSTRUCTORS
# ==========================================================
elif page == "Top Instructors":
    st.subheader("🏆 Top Instructors Leaderboard")

    limit = st.slider("Select Top Instructors Limit", 1, 50, 5)
    top_data = fetch_data(f"/top-instructors?limit={limit}")

    if top_data:
       df_top = pd.DataFrame(top_data)
       st.dataframe(df_top, use_container_width=True)


# ==========================================================
# 3) Teacher vs Course Rating Scatter
# ==========================================================
elif page == "Rating Analysis":
      st.subheader("📈 Teacher Rating vs Course Rating")

      tc_data = fetch_data("/teacher-vs-course-rating")

      if tc_data:
         corr = tc_data["correlation"]
         df_tc = pd.DataFrame(tc_data["data_points"])

         st.write(f"Correlation between TeacherRating and CourseRating: **{corr}**")

         fig = plt.figure()
         plt.scatter(df_tc["TeacherRating"], df_tc["CourseRating"])
         plt.xlabel("Teacher Rating")
         plt.ylabel("Course Rating")
         st.pyplot(fig)


# ==========================================================
# 4) Enrollments by Rating Tier
# ==========================================================
elif page == "Enrollments":
    st.subheader("📊 Enrollments by Instructor Rating Tier")

    tier_data = fetch_data("/enrollments-by-rating-tier")

    if tier_data:
        df_tier = pd.DataFrame(tier_data)

        # Fix order of tiers
        order = ["Low Rated (<3.5)", "Mid Rated (3.5 - 4.49)", "High Rated (>=4.5)"]
        df_tier["RatingTier"] = pd.Categorical(
            df_tier["RatingTier"], categories=order, ordered=True
        )
        df_tier = df_tier.sort_values("RatingTier")

        # -----------------------
        # BAR CHART
        # -----------------------
        fig, ax = plt.subplots(figsize=(7, 4))

        colors = ["#ff6b6b", "#feca57", "#1dd1a1"]  # red, yellow, green
        bars = ax.bar(df_tier["RatingTier"], df_tier["TotalEnrollments"], color=colors)

        ax.set_xlabel("Instructor Rating Tier")
        ax.set_ylabel("Total Enrollments")
        ax.set_title("Enrollments by Instructor Rating Tier")
        plt.xticks(rotation=15)

        

        st.pyplot(fig)

        # -----------------------
        # PIE CHART
        # -----------------------
        fig, ax = plt.subplots(figsize=(6, 6))

        ax.pie(
            df_tier["TotalEnrollments"],
            labels=df_tier["RatingTier"],
            autopct="%1.0f%%",
            startangle=90,
            colors=["#0B3D91", "#1E88E5", "#90CAF9"],
            wedgeprops={"edgecolor": "white", "linewidth": 2},
        )

        ax.set_title("Enrollment Share by Rating Tier", fontsize=14, fontweight="bold")
        st.pyplot(fig)

        st.dataframe(df_tier, use_container_width=True)

    else:
        st.warning("No enrollment tier data received from backend.")





# ==========================================================
# 5) Expertise Performance
# ==========================================================
elif page == "Expertise Insights":
    st.subheader("🧠 Expertise-wise Performance")

    expertise_data = fetch_data("/expertise-performance")

    if expertise_data:
       df_expertise = pd.DataFrame(expertise_data)

    # dropdown options
       expertise_list = ["All"] + sorted(df_expertise["Expertise"].unique().tolist())
       selected = st.selectbox("Filter Expertise", expertise_list)

    # apply filter
       if selected != "All":
           df_expertise = df_expertise[df_expertise["Expertise"] == selected]

    # show table
       st.dataframe(df_expertise, use_container_width=True)

    # bar chart
    fig = plt.figure()
    plt.bar(df_expertise["Expertise"], df_expertise["avg_course_rating"])
    plt.xlabel("Expertise")
    plt.ylabel("Avg Course Rating")
    plt.xticks(rotation=30)
    st.pyplot(fig)

elif page == "Consistency":
    st.subheader("📌 Instructor Rating Consistency (Reliability)")

    data = fetch_data("/rating-consistency")

    if data:
        df = pd.DataFrame(data)

        st.dataframe(df, use_container_width=True)

        # Plot top 10 most consistent
        top = df.sort_values("consistency_score", ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(top["TeacherName"], top["consistency_score"], color="purple")
        ax.set_xlabel("Consistency Score (Higher = More Reliable)")
        ax.set_ylabel("Instructor")
        ax.set_title("Top 10 Most Consistent Instructors")
        st.pyplot(fig)
else:
    st.warning("No data received from backend.")

