# ================= IMPORTS =================
import streamlit as st
import pandas as pd
from datetime import date


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="NutriCalci Pro",
    page_icon="🥗",
    layout="wide"
)


# ================= LOAD DATA =================
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
        .str.replace(" ", "_")
        .str.replace("__", "_")
        .str.strip("_")
    )

    required = [
        "dish_name","calories","carbohydrates",
        "protein","fats","fibre","free_sugar","sodium"
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    numeric_cols = required[1:]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df = df.dropna()

    return df


df = load_data()


# ================= SESSION STATE =================
defaults = {
    "daily_calories": 0.0,
    "daily_protein": 0.0,
    "daily_carbs": 0.0,
    "daily_fat": 0.0,
    "daily_fibre": 0.0,
    "daily_sodium": 0.0,
    "weekly_log": {},
    "weight_log": {}
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ================= TITLE =================
st.title("NutriCalci Pro")
st.caption("Structured Nutrition Tracking")


tabs = st.tabs([
    "Log Food",
    "Daily Overview",
    "Weekly Trends",
    "Body Metrics"
])


# =========================================================
# TAB 1 — LOG FOOD
# =========================================================
with tabs[0]:

    meal_type = st.selectbox(
        "Meal Category",
        ["Breakfast", "Lunch", "Dinner", "Snacks"]
    )

    dish = st.selectbox(
        "Select Dish",
        sorted(df["dish_name"].unique())
    )

    quantity = st.number_input(
        "Quantity (grams)",
        min_value=1,
        max_value=5000,
        value=100
    )

    if st.button("Calculate & Log"):

        row = df[df["dish_name"] == dish].iloc[0]
        scale = quantity / 100

        calories = row["calories"] * scale
        carbs = row["carbohydrates"] * scale
        protein = row["protein"] * scale
        fat = row["fats"] * scale
        fibre = row["fibre"] * scale
        sodium = row["sodium"] * scale

        # Update daily totals
        st.session_state.daily_calories += calories
        st.session_state.daily_protein += protein
        st.session_state.daily_carbs += carbs
        st.session_state.daily_fat += fat
        st.session_state.daily_fibre += fibre
        st.session_state.daily_sodium += sodium

        st.success(f"{meal_type} logged.")

        # Save to weekly log
        today = str(date.today())
        if today not in st.session_state.weekly_log:
            st.session_state.weekly_log[today] = 0

        st.session_state.weekly_log[today] += calories


# =========================================================
# TAB 2 — DAILY OVERVIEW
# =========================================================
with tabs[1]:

    st.subheader("Daily Summary")

    total_cal = st.session_state.daily_calories
    total_protein = st.session_state.daily_protein
    total_carbs = st.session_state.daily_carbs
    total_fat = st.session_state.daily_fat

    st.metric("Calories", f"{total_cal:.0f}")
    st.metric("Protein (g)", f"{total_protein:.1f}")
    st.metric("Carbs (g)", f"{total_carbs:.1f}")
    st.metric("Fat (g)", f"{total_fat:.1f}")

    st.divider()

    # Fiber + Sodium
    st.subheader("Micronutrient Monitoring")

    fibre_goal = 25
    sodium_limit = 2300

    st.write(f"Fibre: {st.session_state.daily_fibre:.1f} g "
             f"({(st.session_state.daily_fibre/fibre_goal)*100:.0f}% of goal)")

    st.write(f"Sodium: {st.session_state.daily_sodium:.0f} mg "
             f"({(st.session_state.daily_sodium/sodium_limit)*100:.0f}% of limit)")

    if st.session_state.daily_sodium > sodium_limit:
        st.error("Sodium above recommended limit.")

    st.divider()

    # Custom Calorie Adjustment
    st.subheader("Calorie Adjustment")

    adjustment = st.slider(
        "Calorie Adjustment",
        min_value=-500,
        max_value=500,
        value=0
    )

    st.write(f"Adjusted target = Maintenance ± {adjustment} kcal")

    st.divider()

    # Macro Target Customization
    st.subheader("Macro Target Comparison")

    target_carbs = st.slider("Target Carbs %", 10, 70, 40)
    target_protein = st.slider("Target Protein %", 10, 50, 30)
    target_fat = st.slider("Target Fat %", 10, 50, 30)

    total_macro_cals = (total_carbs*4 + total_protein*4 + total_fat*9)

    if total_macro_cals > 0:
        actual_carbs = (total_carbs*4/total_macro_cals)*100
        actual_protein = (total_protein*4/total_macro_cals)*100
        actual_fat = (total_fat*9/total_macro_cals)*100

        st.write(f"Carbs deviation: {actual_carbs - target_carbs:.1f}%")
        st.write(f"Protein deviation: {actual_protein - target_protein:.1f}%")
        st.write(f"Fat deviation: {actual_fat - target_fat:.1f}%")


    if st.button("Reset Day"):
        for k in defaults:
            if k != "weekly_log" and k != "weight_log":
                st.session_state[k] = 0.0
        st.success("Day reset.")


# =========================================================
# TAB 3 — WEEKLY TRENDS
# =========================================================
with tabs[2]:

    st.subheader("Weekly Calorie Trend")

    if st.session_state.weekly_log:
        weekly_df = pd.DataFrame(
            list(st.session_state.weekly_log.items()),
            columns=["Date", "Calories"]
        ).sort_values("Date")

        st.line_chart(weekly_df.set_index("Date"))
    else:
        st.info("No data logged yet.")


# =========================================================
# TAB 4 — BODY METRICS
# =========================================================
with tabs[3]:

    st.subheader("Body Weight Tracker")

    today_weight = st.number_input(
        "Enter Today's Weight (kg)",
        min_value=30.0,
        max_value=200.0,
        value=70.0
    )

    if st.button("Save Weight"):
        st.session_state.weight_log[str(date.today())] = today_weight
        st.success("Weight saved.")

    if st.session_state.weight_log:
        weight_df = pd.DataFrame(
            list(st.session_state.weight_log.items()),
            columns=["Date", "Weight"]
        ).sort_values("Date")

        st.line_chart(weight_df.set_index("Date"))

    st.divider()

    st.subheader("BMI Calculator")

    height = st.number_input("Height (cm)", min_value=50.0, value=170.0)

    height_m = height / 100
    bmi = today_weight / (height_m ** 2)

    st.metric("BMI", f"{bmi:.2f}")

    if bmi < 18.5:
        st.warning("Underweight")
    elif bmi < 25:
        st.success("Normal weight")
    elif bmi < 30:
        st.warning("Overweight")
    else:
        st.error("Obese")

    st.caption("BMI is a screening tool, not a medical diagnosis.")
