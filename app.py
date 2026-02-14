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
        "protein": 120,
        "carbs": 250
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
    "Weekly Progress",
    "Smart Goal Recommendation"
])


# ======================================================
# TAB 1 — NUTRITION CALCULATOR
# ======================================================
with tabs[0]:

    dish = st.selectbox(
        "Dish Name",
        sorted(df["dish_name"].unique())
    )

    qty_per_serv = st.number_input(
        "Quantity per Serving (grams)",
        min_value=1,
        max_value=5000,
        value=100
    )

    servings = st.number_input(
        "Number of Servings",
        min_value=1,
        max_value=50,
        value=1
    )

    if st.button("Calculate Nutrition"):

        row = df[df["dish_name"] == dish]
        if row.empty:
            st.error("Dish not found.")
            st.stop()

        row = row.iloc[0]
        scale = (qty_per_serv * servings) / 100

        st.session_state.last_calculation = {
            "calories": row["calories"] * scale,
            "carbs": row["carbohydrates"] * scale,
            "protein": row["protein"] * scale,
            "fat": row["fats"] * scale
        }

    if st.session_state.last_calculation:
        r = st.session_state.last_calculation

        st.metric("Calories", f"{r['calories']:.2f}")
        st.metric("Protein", f"{r['protein']:.2f}")
        st.metric("Carbs", f"{r['carbs']:.2f}")

        if st.button("Add to Daily Intake"):
            for k in r:
                st.session_state.daily[k] += r[k]
            st.success("Added to daily intake.")


# ======================================================
# TAB 2 — CUSTOM RECIPE BUILDER
# ======================================================
with tabs[1]:

    selected = st.multiselect(
        "Select Ingredients",
        sorted(df["dish_name"].unique())
    )

    total = {"calories":0, "carbs":0, "protein":0, "fat":0}

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
            total["calories"] += row["calories"] * scale
            total["carbs"] += row["carbohydrates"] * scale
            total["protein"] += row["protein"] * scale
            total["fat"] += row["fats"] * scale

    if selected:
        st.metric("Calories", f"{total['calories']:.2f}")
        st.metric("Protein", f"{total['protein']:.2f}")
        st.metric("Carbs", f"{total['carbs']:.2f}")

        if st.button("Add Recipe to Daily Intake"):
            for k in total:
                st.session_state.daily[k] += total[k]
            st.success("Recipe logged.")


# ======================================================
# TAB 3 — DAILY TRACKER (SMART % + LEADING NUTRIENT)
# ======================================================
with tabs[2]:

    daily = st.session_state.daily
    goals = st.session_state.recommended_goals

    calorie_goal = st.number_input("Calorie Goal", value=int(goals["calories"]))
    protein_goal = st.number_input("Protein Goal (g)", value=int(goals["protein"]))
    carb_goal = st.number_input("Carb Goal (g)", value=int(goals["carbs"]))

    # Percent calculations (safe)
    cal_pct = min(daily["calories"]/calorie_goal,1.0) if calorie_goal else 0
    prot_pct = min(daily["protein"]/protein_goal,1.0) if protein_goal else 0
    carb_pct = min(daily["carbs"]/carb_goal,1.0) if carb_goal else 0

    st.metric("Calories", f"{daily['calories']:.2f} kcal",
              delta=f"{cal_pct*100:.1f}% of goal")
    st.progress(cal_pct)

    st.metric("Protein", f"{daily['protein']:.2f} g",
              delta=f"{prot_pct*100:.1f}% of goal")
    st.progress(prot_pct)

    st.metric("Carbs", f"{daily['carbs']:.2f} g",
              delta=f"{carb_pct*100:.1f}% of goal")
    st.progress(carb_pct)

    # Determine leading nutrient
    percentages = {
        "Calories": cal_pct,
        "Protein": prot_pct,
        "Carbs": carb_pct
    }

    leading = max(percentages, key=percentages.get)
    st.info(f"Most completed nutrient today: **{leading}**")

    if st.button("Save Today's Data"):
        st.session_state.history[str(date.today())] = {
            "calories": daily["calories"],
            "protein": daily["protein"],
            "carbs": daily["carbs"],
            "goal": calorie_goal
        }
        st.success("Saved to weekly history.")




# ======================================================
# TAB 5 — SMART GOAL RECOMMENDATION
# ======================================================
with tabs[4]:

    weight = st.number_input("Weight (kg)", value=70.0)
    height = st.number_input("Height (cm)", value=170.0)
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
    carbs = (target * 0.5) / 4

    st.metric("Maintenance", f"{maintenance:.0f}")
    st.metric("Recommended Calories", f"{target:.0f}")
    st.metric("Recommended Protein", f"{protein:.0f}")
    st.metric("Recommended Carbs", f"{carbs:.0f}")

    if st.button("Apply Goals"):
        st.session_state.recommended_goals["calories"] = target
        st.session_state.recommended_goals["protein"] = protein
        st.session_state.recommended_goals["carbs"] = carbs
        st.success("Goals applied.")

