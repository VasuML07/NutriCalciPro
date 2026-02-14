# ================= IMPORTS =================
import streamlit as st
import pandas as pd


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

if "last_calculation" not in st.session_state:
    st.session_state.last_calculation = None


# ================= TITLE =================
st.title("🥗 NutriCalci Pro")
st.caption("Smart Nutrition + Daily Tracking + Health Tools")

tabs = st.tabs([
    "Nutrition Calculator",
    "Custom Recipe Builder",
    "Daily Tracker",
    "BMI Calculator"
])


# ======================================================
# TAB 1 — NUTRITION CALCULATOR (FIXED)
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

    if st.button("Calculate Nutrition", key="calc_btn"):

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

    # ---- Display results if available ----
    if st.session_state.last_calculation:

        r = st.session_state.last_calculation

        st.subheader("Nutrition Breakdown")
        st.write(f"Total Quantity: {r['quantity']} g")

        c1, c2, c3 = st.columns(3)
        c1.metric("Calories", f"{r['calories']:.2f} kcal")
        c2.metric("Carbs", f"{r['carbs']:.2f} g")
        c3.metric("Protein", f"{r['protein']:.2f} g")

        c4, c5, c6, c7 = st.columns(4)
        c4.metric("Fat", f"{r['fat']:.2f} g")
        c5.metric("Fibre", f"{r['fibre']:.2f} g")
        c6.metric("Sugar", f"{r['sugar']:.2f} g")
        c7.metric("Sodium", f"{r['sodium']:.2f} mg")

        if st.button("Add to Daily Intake", key="add_single"):

            st.session_state.daily["calories"] += r["calories"]
            st.session_state.daily["protein"] += r["protein"]
            st.session_state.daily["carbs"] += r["carbs"]
            st.session_state.daily["fat"] += r["fat"]

            st.success("Added to daily intake.")


# ======================================================
# TAB 3 — DAILY TRACKER
# ======================================================
with tabs[2]:

    st.subheader("Daily Nutrition Tracker")

    daily = st.session_state.daily

    calorie_goal = st.number_input(
        "Daily Calorie Goal (kcal)",
        min_value=1000,
        max_value=6000,
        value=2000,
        key="cal_goal"
    )

    calories_remaining = calorie_goal - daily["calories"]
    percent = min(daily["calories"] / calorie_goal, 1.0)

    c1, c2, c3 = st.columns(3)
    c1.metric("Consumed", f"{daily['calories']:.2f} kcal")
    c2.metric("Goal", f"{calorie_goal:.0f} kcal")
    c3.metric("Remaining", f"{calories_remaining:.2f} kcal")

    st.progress(percent)

    st.divider()

    protein_goal = st.number_input(
        "Daily Protein Goal (g)",
        min_value=20,
        max_value=300,
        value=120,
        key="protein_goal"
    )

    protein_remaining = protein_goal - daily["protein"]
    protein_percent = min(daily["protein"] / protein_goal, 1.0)

    p1, p2, p3 = st.columns(3)
    p1.metric("Consumed", f"{daily['protein']:.2f} g")
    p2.metric("Goal", f"{protein_goal:.0f} g")
    p3.metric("Remaining", f"{protein_remaining:.2f} g")

    st.progress(protein_percent)

    st.divider()

    if st.button("Reset Daily Data"):
        st.session_state.daily = {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0
        }
        st.success("Daily data reset.")
