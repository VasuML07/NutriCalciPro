# Importing required libraries
import streamlit as st
import pandas as pd
import numpy as np
#  Page Configuration 
st.set_page_config(
    page_title="NutriCalci Pro",
    page_icon="🥗",
    layout="wide"
)
#  Load Dataset 
@st.cache_data
def load_data():
    df = pd.read_csv("database.csv")
    # Clean column names safely
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\(.*?\)", "", regex=True)
        .str.replace(" ", "_")
        .str.replace("__", "_")
        .str.strip("_")
    )
    df = df.dropna()
    return df
df = load_data()
#  Session State 
if "daily_calories" not in st.session_state:
    st.session_state.daily_calories = 0
if "recipe_items" not in st.session_state:
    st.session_state.recipe_items = []
#  App Title 
st.title("🥗 NutriCalci Pro")
st.caption("Smart Nutrition + Daily Tracking + Health Tools")
tabs = st.tabs([
    "Nutrition Calculator",
    "Custom Recipe Builder",
    "Daily Tracker",
    "BMI Calculator"
])
# 🥗 TAB 1 — Nutrition Calculator
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
            value=100
        )
    with col3:
        servings = st.number_input(
            "Number of Servings",
            min_value=1,
            value=1
        )
    if st.button("Calculate Nutrition 🔥"):
        food_row = df[df["dish_name"] == dish]
        if not food_row.empty:
            food_row = food_row.iloc[0]
            # Total quantity consumed
            total_quantity = quantity * servings
            scale = total_quantity / 100
            calories = food_row["calories"] * scale
            carbs = food_row["carbohydrates"] * scale
            protein = food_row["protein"] * scale
            fat = food_row["fats"] * scale
            fiber = food_row["fibre"] * scale
            sugar = food_row["free_sugar"] * scale
            sodium = food_row["sodium"] * scale
            st.session_state.daily_calories += calories
            st.session_state.daily_protein += protein
            st.session_state.daily_carbs += carbs
            st.session_state.daily_fat += fat
            st.subheader("📊 Nutrition Breakdown")
            st.write(f"Total Consumed: **{total_quantity} grams**")
            c1, c2, c3 = st.columns(3)
            c1.metric("Calories", f"{calories:.2f} kcal")
            c2.metric("Carbs", f"{carbs:.2f} g")
            c3.metric("Protein", f"{protein:.2f} g")
            c4, c5, c6, c7 = st.columns(4)
            c4.metric("Fat", f"{fat:.2f} g")
            c5.metric("Fiber", f"{fiber:.2f} g")
            c6.metric("Sugar", f"{sugar:.2f} g")
            c7.metric("Sodium", f"{sodium:.2f} mg")
            macro_data = pd.DataFrame({
                "Nutrient": ["Carbs", "Protein", "Fat"],
                "Amount": [carbs, protein, fat]
            })
            st.bar_chart(macro_data.set_index("Nutrient"))
# 🍲 TAB 2 — Custom Recipe Builder
with tabs[1]:
    st.subheader("Build Your Own Recipe")
    # User selects multiple dishes
    selected_dishes = st.multiselect(
        "Select Ingredients",
        sorted(df["dish_name"].unique())
    )
    total_cal = total_carbs = total_protein = total_fat = 0
    if selected_dishes:
        st.write("### Enter Quantity for Each Ingredient")
        for dish in selected_dishes:
            qty = st.number_input(
                f"Quantity for {dish} (grams)",
                min_value=1,
                value=100,
                key=dish
            )
            row = df[df["dish_name"] == dish].iloc[0]
            scale = qty / 100
            total_cal += row["calories"] * scale
            total_carbs += row["carbohydrates"] * scale
            total_protein += row["protein"] * scale
            total_fat += row["fats"] * scale
        st.divider()
        st.subheader("Recipe Total Nutrition")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", f"{total_cal:.2f} kcal")
        c2.metric("Carbs", f"{total_carbs:.2f} g")
        c3.metric("Protein", f"{total_protein:.2f} g")
        c4.metric("Fat", f"{total_fat:.2f} g")
        # Optional macro chart
        macro_data = pd.DataFrame({
            "Nutrient": ["Carbs", "Protein", "Fat"],
            "Amount": [total_carbs, total_protein, total_fat]
        })
        st.bar_chart(macro_data.set_index("Nutrient"))
        if st.button("Add Recipe to Daily Intake"):
         st.session_state.daily_calories += total_cal
         st.session_state.daily_protein += total_protein
         st.session_state.daily_carbs += total_carbs
         st.session_state.daily_fat += total_fat
         st.success("Recipe added to daily intake!")
# 📈 TAB 3 — Daily Tracker + Advanced Features
with tabs[2]:
    st.subheader("Daily Nutrition Tracker")
    #Basic Daily Tracking 
    total_calories = st.session_state.daily_calories
    st.metric(
        "Total Calories Consumed Today",
        f"{total_calories:.2f} kcal"
    )
    # Calorie Goal
    calorie_goal = st.number_input(
        "Daily Calorie Goal",
        min_value=1000,
        value=2000
    )
    calorie_progress = min(total_calories / calorie_goal, 1.0)
    st.progress(calorie_progress)
    # Protein Goal Tracker
    st.divider()
    st.subheader("Protein Goal Tracker")
    # We calculate protein consumed from recipe builder + calculator
    # To do this properly, you should track protein in session state
    if "daily_protein" not in st.session_state:
        st.session_state.daily_protein = 0
    protein_goal = st.number_input(
        "Daily Protein Goal (g)",
        min_value=20,
        value=120
    )
    st.metric(
        "Protein Consumed Today",
        f"{st.session_state.daily_protein:.2f} g"
    )
    protein_progress = min(st.session_state.daily_protein / protein_goal, 1.0)
    st.progress(protein_progress)
    #  Macro Percentage Breakdown
    st.divider()
    st.subheader("Macro Percentage Breakdown")
    # You need total carbs, protein, fat stored
    if "daily_carbs" not in st.session_state:
        st.session_state.daily_carbs = 0
    if "daily_fat" not in st.session_state:
        st.session_state.daily_fat = 0
    # Calculate calorie contribution from macros
    carb_cals = st.session_state.daily_carbs * 4
    protein_cals = st.session_state.daily_protein * 4
    fat_cals = st.session_state.daily_fat * 9
    total_macro_cals = carb_cals + protein_cals + fat_cals
    if total_macro_cals > 0:
        carb_percent = (carb_cals / total_macro_cals) * 100
        protein_percent = (protein_cals / total_macro_cals) * 100
        fat_percent = (fat_cals / total_macro_cals) * 100
        st.write(f"Carbs: **{carb_percent:.1f}%**")
        st.write(f"Protein: **{protein_percent:.1f}%**")
        st.write(f"Fat: **{fat_percent:.1f}%**")
    # Surplus / Deficit Calculator
    st.divider()
    st.subheader("Calorie Surplus / Deficit Calculator")
    goal_type = st.selectbox(
        "Your Goal",
        ["Maintain Weight", "Weight Loss", "Weight Gain"]
    )
    weight = st.number_input("Weight (kg)", min_value=30.0, value=70.0)
    activity_level = st.selectbox(
        "Activity Level",
        [
            ("Sedentary", 1.2),
            ("Lightly Active", 1.375),
            ("Moderately Active", 1.55),
            ("Very Active", 1.725),
            ("Extra Active", 1.9)
        ],
        format_func=lambda x: x[0]
    )
    # Basic BMR using Mifflin-St Jeor (assuming male, simplified)
    bmr = 10 * weight + 6.25 * 170 - 5 * 25 + 5  # height=170, age=25 default
    maintenance_calories = bmr * activity_level[1]
    if goal_type == "Weight Loss":
        target_calories = maintenance_calories - 500
    elif goal_type == "Weight Gain":
        target_calories = maintenance_calories + 500
    else:
        target_calories = maintenance_calories
    st.metric("Estimated Maintenance Calories", f"{maintenance_calories:.0f} kcal")
    st.metric("Recommended Daily Target", f"{target_calories:.0f} kcal")
    difference = total_calories - target_calories
    if difference > 0:
        st.error(f"You are in a surplus of {difference:.0f} kcal")
    else:
        st.success(f"You are in a deficit of {abs(difference):.0f} kcal")
    if st.button("Reset Daily Calories"):
        st.session_state.daily_calories = 0
        st.session_state.daily_protein = 0
        st.session_state.daily_carbs = 0
        st.session_state.daily_fat = 0
        st.success("Daily values reset.")
# 🧍 TAB 4 — BMI Calculator
with tabs[3]:
    st.subheader("BMI Calculator")
    weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=50.0, value=170.0)
    if st.button("Calculate BMI"):
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
