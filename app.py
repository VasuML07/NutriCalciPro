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

    # Clean column names properly
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
    df = df[df["calories"] >= 0]  # basic validation

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

    if st.button("Calculate Nutrition", key="calc_btn"):

        row = df[df["dish_name"] == dish]

        if row.empty:
            st.error("Dish not found.")
            st.stop()

        row = row.iloc[0]

        total_qty = qty_per_serv * servings
        scale = total_qty / 100

        calories = row["calories"] * scale
        carbs = row["carbohydrates"] * scale
        protein = row["protein"] * scale
        fat = row["fats"] * scale
        fibre = row["fibre"] * scale
        sugar = row["free_sugar"] * scale
        sodium = row["sodium"] * scale

        st.subheader("Nutrition Breakdown")
        st.write(f"Total Quantity: {total_qty} g")

        c1, c2, c3 = st.columns(3)
        c1.metric("Calories", f"{calories:.2f} kcal")
        c2.metric("Carbs", f"{carbs:.2f} g")
        c3.metric("Protein", f"{protein:.2f} g")

        c4, c5, c6, c7 = st.columns(4)
        c4.metric("Fat", f"{fat:.2f} g")
        c5.metric("Fibre", f"{fibre:.2f} g")
        c6.metric("Sugar", f"{sugar:.2f} g")
        c7.metric("Sodium", f"{sodium:.2f} mg")

        if st.button("Add to Daily Intake", key="add_single"):
            st.session_state.daily["calories"] += calories
            st.session_state.daily["protein"] += protein
            st.session_state.daily["carbs"] += carbs
            st.session_state.daily["fat"] += fat
            st.success("Logged.")


# ======================================================
# TAB 2 — CUSTOM RECIPE BUILDER
# ======================================================
with tabs[1]:

    st.subheader("Build Your Own Recipe")

    selected = st.multiselect(
        "Select Ingredients",
        sorted(df["dish_name"].unique()),
        key="recipe_select"
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
        st.divider()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", f"{total['cal']:.2f}")
        c2.metric("Carbs", f"{total['carbs']:.2f} g")
        c3.metric("Protein", f"{total['protein']:.2f} g")
        c4.metric("Fat", f"{total['fat']:.2f} g")

        if st.button("Add Recipe to Daily Intake", key="add_recipe"):
            st.session_state.daily["calories"] += total["cal"]
            st.session_state.daily["protein"] += total["protein"]
            st.session_state.daily["carbs"] += total["carbs"]
            st.session_state.daily["fat"] += total["fat"]
            st.success("Recipe logged.")


# ======================================================
# TAB 3 — DAILY TRACKER (UPDATED)
# ======================================================
with tabs[2]:

    st.subheader("Daily Nutrition Tracker")

    daily = st.session_state.daily

    # ---------------- CALORIE SECTION ----------------
    st.markdown("### Calorie Tracking")

    calorie_goal = st.number_input(
        "Daily Calorie Goal (kcal)",
        min_value=1000,
        max_value=6000,
        value=2000,
        key="cal_goal"
    )

    calories_consumed = daily["calories"]
    calories_remaining = calorie_goal - calories_consumed
    calorie_percent = min(calories_consumed / calorie_goal, 1.0)

    c1, c2, c3 = st.columns(3)
    c1.metric("Consumed", f"{calories_consumed:.2f} kcal")
    c2.metric("Goal", f"{calorie_goal:.0f} kcal")
    c3.metric(
        "Remaining",
        f"{abs(calories_remaining):.2f} kcal",
        delta=f"{calories_remaining:.2f}"
    )

    st.progress(calorie_percent)

    if calories_remaining < 0:
        st.error(f"You are in a surplus of {abs(calories_remaining):.2f} kcal")
    else:
        st.success(f"You have {calories_remaining:.2f} kcal remaining")

    st.divider()

    # ---------------- PROTEIN SECTION ----------------
    st.markdown("### Protein Tracking")

    protein_goal = st.number_input(
        "Daily Protein Goal (g)",
        min_value=20,
        max_value=300,
        value=120,
        key="protein_goal"
    )

    protein_consumed = daily["protein"]
    protein_remaining = protein_goal - protein_consumed
    protein_percent = min(protein_consumed / protein_goal, 1.0)

    p1, p2, p3 = st.columns(3)
    p1.metric("Consumed", f"{protein_consumed:.2f} g")
    p2.metric("Goal", f"{protein_goal:.0f} g")
    p3.metric(
        "Remaining",
        f"{abs(protein_remaining):.2f} g",
        delta=f"{protein_remaining:.2f}"
    )

    st.progress(protein_percent)

    if protein_remaining < 0:
        st.error(f"You exceeded protein goal by {abs(protein_remaining):.2f} g")
    else:
        st.success(f"You need {protein_remaining:.2f} g more protein")

    st.divider()

    # ---------------- MACRO DISTRIBUTION ----------------
    st.markdown("### Macro Distribution")

    carb_cals = daily["carbs"] * 4
    protein_cals = daily["protein"] * 4
    fat_cals = daily["fat"] * 9

    total_macro = carb_cals + protein_cals + fat_cals

    if total_macro > 0:
        st.write(f"Carbs: {(carb_cals/total_macro)*100:.1f}%")
        st.write(f"Protein: {(protein_cals/total_macro)*100:.1f}%")
        st.write(f"Fat: {(fat_cals/total_macro)*100:.1f}%")
    else:
        st.info("No food logged yet.")

    st.divider()

    # ---------------- RESET BUTTON ----------------
    if st.button("Reset Daily Data", key="reset"):
        st.session_state.daily = {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0
        }
        st.success("Daily data reset.")


# ======================================================
# TAB 4 — BMI
# ======================================================
with tabs[3]:

    st.subheader("BMI Calculator")

    w = st.number_input("Weight (kg)", min_value=1.0, value=70.0, key="bmi_w")
    h = st.number_input("Height (cm)", min_value=50.0, value=170.0, key="bmi_h")

    if st.button("Calculate BMI", key="bmi_btn"):

        height_m = h / 100
        bmi = w / (height_m ** 2)

        st.metric("Your BMI", f"{bmi:.2f}")

        if bmi < 18.5:
            st.warning("Underweight")
        elif bmi < 25:
            st.success("Normal weight")
        elif bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")

        st.caption("BMI is a screening tool, not medical advice.")

