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
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    df = df.dropna()
    df = df[df["calories"] >= 0]

    return df


df = load_data()


# ================= SESSION STATE =================
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

if "last_calculation" not in st.session_state:
    st.session_state.last_calculation = None


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
# TAB 1 — NUTRITION CALCULATOR
# ======================================================
with tabs[0]:

    st.subheader("Calculate Dish Nutrition")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        dish = st.selectbox(
            "Dish Name",
            sorted(df["dish_name"].unique()),
            key="dish_select"
        )

    with col2:
        qty_per_serv = st.number_input(
            "Quantity per Serving (grams)",
            min_value=1,
            max_value=5000,
            value=100,
            key="qty_serv"
        )

    with col3:
        servings = st.number_input(
            "Number of Servings",
            min_value=1,
            max_value=50,
            value=1,
            key="servings"
        )

    if st.button("Calculate Nutrition"):

        row = df[df["dish_name"] == dish]
        if row.empty:
            st.error("Dish not found.")
            st.stop()

        row = row.iloc[0]
        total_qty = qty_per_serv * servings
        scale = total_qty / 100

        result = {
            "calories": row["calories"] * scale,
            "carbs": row["carbohydrates"] * scale,
            "protein": row["protein"] * scale,
            "fat": row["fats"] * scale,
            "fibre": row["fibre"] * scale,
            "sugar": row["free_sugar"] * scale,
            "sodium": row["sodium"] * scale,
            "quantity": total_qty
        }

        st.session_state.last_calculation = result

    if st.session_state.last_calculation:
        r = st.session_state.last_calculation

        st.write(f"Total Quantity: {r['quantity']} g")
        st.metric("Calories", f"{r['calories']:.2f} kcal")
        st.metric("Protein", f"{r['protein']:.2f} g")

        if st.button("Add to Daily Intake"):
            st.session_state.daily["calories"] += r["calories"]
            st.session_state.daily["protein"] += r["protein"]
            st.session_state.daily["carbs"] += r["carbs"]
            st.session_state.daily["fat"] += r["fat"]
            st.success("Added to daily intake.")


# ======================================================
# TAB 2 — CUSTOM RECIPE BUILDER
# ======================================================
with tabs[1]:

    st.subheader("Build Your Own Recipe")

    selected = st.multiselect(
        "Select Ingredients",
        sorted(df["dish_name"].unique())
    )

    total = {"cal":0, "carbs":0, "protein":0, "fat":0}

    for dish in selected:
        qty = st.number_input(
            f"{dish} quantity (grams)",
            min_value=1,
            max_value=5000,
            value=100,
            key=f"{dish}_qty"
        )

        row = df[df["dish_name"] == dish]
        if not row.empty:
            row = row.iloc[0]
            scale = qty / 100
            total["cal"] += row["calories"] * scale
            total["carbs"] += row["carbohydrates"] * scale
            total["protein"] += row["protein"] * scale
            total["fat"] += row["fats"] * scale

    if selected:
        st.metric("Calories", f"{total['cal']:.2f}")
        st.metric("Protein", f"{total['protein']:.2f}")

        if st.button("Add Recipe to Daily Intake"):
            st.session_state.daily["calories"] += total["cal"]
            st.session_state.daily["protein"] += total["protein"]
            st.session_state.daily["carbs"] += total["carbs"]
            st.session_state.daily["fat"] += total["fat"]
            st.success("Recipe logged.")


# ======================================================
# TAB 3 — DAILY TRACKER
# ======================================================
with tabs[2]:

    daily = st.session_state.daily

    calorie_goal = st.number_input(
        "Daily Calorie Goal",
        value=int(st.session_state.recommended_goals["calories"])
    )

    protein_goal = st.number_input(
        "Daily Protein Goal",
        value=int(st.session_state.recommended_goals["protein"])
    )

    st.metric("Calories Consumed", f"{daily['calories']:.2f}")
    st.metric("Protein Consumed", f"{daily['protein']:.2f}")

    st.progress(min(daily["calories"]/calorie_goal,1.0))
    st.progress(min(daily["protein"]/protein_goal,1.0))

    if st.button("Save Today's Data"):
        st.session_state.history[str(date.today())] = {
            "calories": daily["calories"],
            "protein": daily["protein"],
            "goal": calorie_goal
        }
        st.success("Saved to weekly history.")


# ======================================================
# TAB 4 — BMI
# ======================================================
with tabs[3]:

    w = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
    h = st.number_input("Height (cm)", min_value=50.0, value=170.0)

    if st.button("Calculate BMI"):
        bmi = w / ((h/100) ** 2)
        st.metric("BMI", f"{bmi:.2f}")


# ======================================================
# TAB 5 — WEEKLY PROGRESS
# ======================================================
with tabs[4]:

    history = st.session_state.history

    if not history:
        st.info("No saved data yet.")
    else:
        df_history = pd.DataFrame.from_dict(history, orient="index")
        df_history.index = pd.to_datetime(df_history.index)
        df_history = df_history.sort_index()

        last_week = date.today() - timedelta(days=7)
        df_week = df_history[df_history.index >= pd.to_datetime(last_week)]

        st.line_chart(df_week["calories"])
        st.line_chart(df_week["protein"])

        st.metric("Weekly Avg Calories", f"{df_week['calories'].mean():.2f}")
        st.metric("Weekly Avg Protein", f"{df_week['protein'].mean():.2f}")

        weekly_diff = (df_week["calories"] - df_week["goal"]).sum()

        if weekly_diff > 0:
            st.error(f"Weekly Surplus: {weekly_diff:.2f}")
        else:
            st.success(f"Weekly Deficit: {abs(weekly_diff):.2f}")


# ======================================================
# TAB 6 — SMART GOAL RECOMMENDATION
# ======================================================
with tabs[5]:

    weight = st.number_input("Weight", value=70.0)
    height = st.number_input("Height", value=170.0)
    age = st.number_input("Age", value=25)
    gender = st.selectbox("Gender", ["Male","Female"])
    activity = st.selectbox("Activity Level",
                            ["Sedentary","Light","Moderate","Active"])

    multiplier = {
        "Sedentary":1.2,
        "Light":1.375,
        "Moderate":1.55,
        "Active":1.725
    }[activity]

    goal = st.selectbox("Goal Type",
                        ["Fat Loss","Muscle Gain","Maintenance"])

    if gender=="Male":
        bmr = 10*weight + 6.25*height - 5*age + 5
    else:
        bmr = 10*weight + 6.25*height - 5*age - 161

    maintenance = bmr * multiplier

    if goal=="Fat Loss":
        target = maintenance - 400
    elif goal=="Muscle Gain":
        target = maintenance + 250
    else:
        target = maintenance

    protein = weight * 1.8

    st.metric("Maintenance", f"{maintenance:.0f}")
    st.metric("Recommended Calories", f"{target:.0f}")
    st.metric("Recommended Protein", f"{protein:.0f}")

    if st.button("Apply Goals"):
        st.session_state.recommended_goals["calories"] = target
        st.session_state.recommended_goals["protein"] = protein
        st.success("Goals applied.")
