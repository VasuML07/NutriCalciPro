# ================= IMPORTS =================
import streamlit as st
import pandas as pd


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="NutriCalci Pro",
    page_icon="🥗",
    layout="wide"
)


# ================= LOAD DATA SAFELY =================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("database.csv")
    except FileNotFoundError:
        st.error("database.csv file not found.")
        st.stop()

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\(.*?\)", "", regex=True)
        .str.replace(" ", "_")
        .str.replace("__", "_")
        .str.strip("_")
    )

    required_columns = [
        "dish_name",
        "calories",
        "carbohydrates",
        "protein",
        "fats",
        "fibre",
        "free_sugar",
        "sodium"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        st.stop()

    # Force numeric columns
    numeric_cols = required_columns[1:]
    df[numeric_cols] = df[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    df = df.dropna()

    return df


df = load_data()


# ================= SESSION STATE INIT =================
defaults = {
    "daily_calories": 0.0,
    "daily_protein": 0.0,
    "daily_carbs": 0.0,
    "daily_fat": 0.0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        dish = st.selectbox(
            "Select Dish",
            sorted(df["dish_name"].unique())
        )

    with col2:
        quantity = st.number_input(
            "Quantity per Serving (grams)",
            min_value=1,
            max_value=5000,
            value=100
        )

    with col3:
        servings = st.number_input(
            "Number of Servings",
            min_value=1,
            max_value=20,
            value=1
        )

    if st.button("Calculate Nutrition", key="calc_btn"):

        row = df[df["dish_name"] == dish].iloc[0]

        total_quantity = quantity * servings
        scale = total_quantity / 100

        calories = row["calories"] * scale
        carbs = row["carbohydrates"] * scale
        protein = row["protein"] * scale
        fat = row["fats"] * scale
        fiber = row["fibre"] * scale
        sugar = row["free_sugar"] * scale
        sodium = row["sodium"] * scale

        st.subheader("Nutrition Breakdown")
        st.write(f"Total Consumed: {total_quantity} grams")

        c1, c2, c3 = st.columns(3)
        c1.metric("Calories", f"{calories:.2f} kcal")
        c2.metric("Carbs", f"{carbs:.2f} g")
        c3.metric("Protein", f"{protein:.2f} g")

        c4, c5, c6, c7 = st.columns(4)
        c4.metric("Fat", f"{fat:.2f} g")
        c5.metric("Fiber", f"{fiber:.2f} g")
        c6.metric("Sugar", f"{sugar:.2f} g")
        c7.metric("Sodium", f"{sodium:.2f} mg")

        if st.button("Add to Daily Intake", key="add_single"):
            st.session_state.daily_calories += calories
            st.session_state.daily_protein += protein
            st.session_state.daily_carbs += carbs
            st.session_state.daily_fat += fat
            st.success("Logged successfully.")


# ======================================================
# TAB 2 — CUSTOM RECIPE BUILDER
# ======================================================
with tabs[1]:

    st.subheader("Build Your Own Recipe")

    selected_dishes = st.multiselect(
        "Select Ingredients",
        sorted(df["dish_name"].unique())
    )

    total_cal = total_carbs = total_protein = total_fat = 0.0

    if selected_dishes:

        for dish in selected_dishes:

            qty = st.number_input(
                f"{dish} quantity (grams)",
                min_value=1,
                max_value=5000,
                value=100,
                key=f"{dish}_qty"
            )

            row = df[df["dish_name"] == dish].iloc[0]
            scale = qty / 100

            total_cal += row["calories"] * scale
            total_carbs += row["carbohydrates"] * scale
            total_protein += row["protein"] * scale
            total_fat += row["fats"] * scale

        st.divider()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", f"{total_cal:.2f}")
        c2.metric("Carbs", f"{total_carbs:.2f} g")
        c3.metric("Protein", f"{total_protein:.2f} g")
        c4.metric("Fat", f"{total_fat:.2f} g")

        if st.button("Add Recipe to Daily Intake", key="add_recipe"):
            st.session_state.daily_calories += total_cal
            st.session_state.daily_protein += total_protein
            st.session_state.daily_carbs += total_carbs
            st.session_state.daily_fat += total_fat
            st.success("Recipe logged.")


# ======================================================
# TAB 3 — DAILY TRACKER
# ======================================================
with tabs[2]:

    st.subheader("Daily Nutrition Tracker")

    total_calories = st.session_state.daily_calories
    st.metric("Calories Today", f"{total_calories:.2f} kcal")

    calorie_goal = st.number_input(
        "Daily Calorie Goal",
        min_value=1000,
        max_value=6000,
        value=2000
    )

    progress = total_calories / calorie_goal if calorie_goal > 0 else 0
    st.progress(min(progress, 1.0))

    st.divider()
    st.subheader("Protein Tracker")

    protein_goal = st.number_input(
        "Daily Protein Goal (g)",
        min_value=20,
        max_value=300,
        value=120
    )

    st.metric(
        "Protein Today",
        f"{st.session_state.daily_protein:.2f} g"
    )

    protein_progress = (
        st.session_state.daily_protein / protein_goal
        if protein_goal > 0 else 0
    )
    st.progress(min(protein_progress, 1.0))

    st.divider()
    st.subheader("Macro Distribution")

    carb_cals = st.session_state.daily_carbs * 4
    protein_cals = st.session_state.daily_protein * 4
    fat_cals = st.session_state.daily_fat * 9

    total_macro_cals = carb_cals + protein_cals + fat_cals

    if total_macro_cals > 0:
        st.write(f"Carbs: {(carb_cals/total_macro_cals)*100:.1f}%")
        st.write(f"Protein: {(protein_cals/total_macro_cals)*100:.1f}%")
        st.write(f"Fat: {(fat_cals/total_macro_cals)*100:.1f}%")

    st.divider()
    st.subheader("Calorie Surplus / Deficit")

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

    activity_choice = st.selectbox(
        "Activity Level",
        list(activity_map.keys())
    )

    multiplier = activity_map[activity_choice]

    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    maintenance = bmr * multiplier

    st.metric("Maintenance Calories", f"{maintenance:.0f} kcal")

    diff = total_calories - maintenance

    if diff > 0:
        st.error(f"Surplus: {diff:.0f} kcal")
    else:
        st.success(f"Deficit: {abs(diff):.0f} kcal")

    if st.button("Reset Daily Data", key="reset_daily"):
        for key in defaults:
            st.session_state[key] = 0.0
        st.success("Daily values reset.")


# ======================================================
# TAB 4 — BMI
# ======================================================
with tabs[3]:

    st.subheader("BMI Calculator")

    weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=50.0, value=170.0)

    if st.button("Calculate BMI", key="bmi_btn"):

        height_m = height / 100
        bmi = weight / (height_m ** 2)

        st.metric("Your BMI", f"{bmi:.2f}")

        if bmi < 18.5:
            st.warning("Underweight")
        elif 18.5 <= bmi < 25:
            st.success("Normal weight")
        elif 25 <= bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")

        st.caption("BMI is a screening tool, not a medical diagnosis.")
