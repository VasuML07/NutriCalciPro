# ================= IMPORTS =================
import streamlit as st
import pandas as pd
from datetime import date, timedelta


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="NutriCalci Pro",
    page_icon="🥗",
    layout="wide"
)


# ================= SAFE DATA LOADING =================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("database.csv")
    except FileNotFoundError:
        st.error("database.csv file not found.")
        st.stop()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\(.*?\)", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )

    required_columns = [
        "dish_name","calories","carbohydrates",
        "protein","fats","fibre","free_sugar","sodium"
    ]

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        st.stop()

    numeric_cols = required_columns[1:]
    df[numeric_cols] = df[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    df = df.dropna()
    df = df[df["calories"] >= 0]

    return df


df = load_data()


# ================= SESSION STATE INIT =================
if "daily" not in st.session_state:
    st.session_state.daily = {
        "calories": 0.0,
        "protein": 0.0,
        "carbs": 0.0,
        "fat": 0.0
    }

if "history" not in st.session_state:
    st.session_state.history = {}

if "recommended_goals" not in st.session_state:
    st.session_state.recommended_goals = {
        "calories": 2000,
        "protein": 120
    }


# ================= TITLE =================
st.title("🥗 NutriCalci Pro")
st.caption("Smart Nutrition + Tracking + Coaching")

tabs = st.tabs([
    "Nutrition Calculator",
    "Custom Recipe Builder",
    "Daily Tracker",
    "BMI Calculator",
    "Weekly Progress",
    "Smart Goal Recommendation"
])


# ======================================================
# TAB 3 — DAILY TRACKER (with SAVE DAY)
# ======================================================
with tabs[2]:

    st.subheader("Daily Nutrition Tracker")

    daily = st.session_state.daily

    calorie_goal = st.number_input(
        "Daily Calorie Goal (kcal)",
        min_value=1000,
        max_value=6000,
        value=int(st.session_state.recommended_goals["calories"]),
        key="cal_goal"
    )

    protein_goal = st.number_input(
        "Daily Protein Goal (g)",
        min_value=20,
        max_value=300,
        value=int(st.session_state.recommended_goals["protein"]),
        key="protein_goal"
    )

    calories_remaining = calorie_goal - daily["calories"]
    protein_remaining = protein_goal - daily["protein"]

    st.metric("Calories Consumed", f"{daily['calories']:.2f} kcal")
    st.metric("Protein Consumed", f"{daily['protein']:.2f} g")

    st.progress(min(daily["calories"] / calorie_goal, 1.0))
    st.progress(min(daily["protein"] / protein_goal, 1.0))

    if st.button("Save Today's Data"):

        today = str(date.today())

        st.session_state.history[today] = {
            "calories": daily["calories"],
            "protein": daily["protein"],
            "goal": calorie_goal
        }

        st.success("Today's data saved to weekly history.")

    if st.button("Reset Daily Data"):
        st.session_state.daily = {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0
        }
        st.success("Daily data reset.")


# ======================================================
# TAB 5 — WEEKLY PROGRESS
# ======================================================
with tabs[4]:

    st.subheader("Weekly Progress & Trends")

    history = st.session_state.history

    if not history:
        st.info("No historical data saved yet.")
    else:
        df_history = pd.DataFrame.from_dict(history, orient="index")
        df_history.index = pd.to_datetime(df_history.index)
        df_history = df_history.sort_index()

        last_7_days = date.today() - timedelta(days=7)
        df_week = df_history[df_history.index >= pd.to_datetime(last_7_days)]

        st.markdown("### Last 7 Days Calorie Trend")
        st.line_chart(df_week["calories"])

        st.markdown("### Last 7 Days Protein Trend")
        st.line_chart(df_week["protein"])

        weekly_avg = df_week.mean()

        st.metric("Weekly Avg Calories", f"{weekly_avg['calories']:.2f}")
        st.metric("Weekly Avg Protein", f"{weekly_avg['protein']:.2f}")

        weekly_surplus = (df_week["calories"] - df_week["goal"]).sum()

        if weekly_surplus > 0:
            st.error(f"Weekly Surplus: {weekly_surplus:.2f} kcal")
        else:
            st.success(f"Weekly Deficit: {abs(weekly_surplus):.2f} kcal")


# ======================================================
# TAB 6 — SMART GOAL RECOMMENDATION
# ======================================================
with tabs[5]:

    st.subheader("Smart Goal Recommendation")

    weight = st.number_input("Weight (kg)", min_value=30.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=120.0, value=170.0)
    age = st.number_input("Age", min_value=10, value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])

    activity_map = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extra Active": 1.9
    }

    activity = st.selectbox("Activity Level", list(activity_map.keys()))
    multiplier = activity_map[activity]

    goal_type = st.selectbox(
        "Goal Type",
        ["Fat Loss", "Muscle Gain", "Maintenance"]
    )

    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    maintenance = bmr * multiplier

    if goal_type == "Fat Loss":
        target_calories = maintenance - 400
    elif goal_type == "Muscle Gain":
        target_calories = maintenance + 250
    else:
        target_calories = maintenance

    protein_recommendation = weight * 1.8

    st.metric("Estimated Maintenance Calories", f"{maintenance:.0f} kcal")
    st.metric("Recommended Daily Calories", f"{target_calories:.0f} kcal")
    st.metric("Recommended Protein", f"{protein_recommendation:.0f} g")

    if st.button("Apply These Goals"):
        st.session_state.recommended_goals["calories"] = target_calories
        st.session_state.recommended_goals["protein"] = protein_recommendation
        st.success("Goals applied to Daily Tracker.")
