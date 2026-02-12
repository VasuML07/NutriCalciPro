🥗 NutriCalci Pro

Intelligent Nutrition Calculator (Python + Streamlit)

📌 Overview

NutriCalci Pro is a Python-based nutrition tracking system that allows users to:

Calculate calories and nutrients from food items

Track daily intake

Monitor macro distribution

Set calorie and protein goals

Estimate calorie surplus or deficit

Calculate BMI

The project is built entirely in Python using Streamlit and focuses on clean architecture, real nutritional logic, and practical usability.

🚀 Features
🥗 Nutrition Calculator

Select food from dataset

Enter quantity and servings

Automatically calculate:

Calories

Protein

Carbohydrates

Fat

Fiber

Sugar

Sodium

Displays macro distribution chart

🍲 Custom Recipe Builder

Select multiple ingredients

Enter quantity for each

Automatically calculate total recipe nutrition

View combined macro breakdown

📈 Daily Tracker

Tracks total daily calories

Tracks total daily protein, carbs, and fat

Displays progress toward calorie goal

Displays progress toward protein goal

Shows macro percentage breakdown:

% Calories from Carbs

% from Protein

% from Fat

⚖️ Surplus / Deficit Calculator

User selects goal:

Maintain

Weight Loss

Weight Gain

Enter weight

Select activity level

Calculates:

Estimated maintenance calories

Recommended target calories

Surplus or deficit amount

🧍 BMI Calculator

Enter weight and height

Calculates BMI

Displays classification

🧠 Technical Stack

Python 3.11+

Streamlit

Pandas

NumPy

Optional (future expansion):

Scikit-learn

TensorFlow / PyTorch (for ANN-based custom dish estimation)

📊 Dataset

The application uses a cleaned nutrition dataset (database.csv) containing:

Dish Name

Calories

Protein

Carbohydrates

Fat

Fiber

Micronutrients

All values are standardized per 100 grams.

📁 Project Structure
NUTRICALCI/
│
├── app.py
├── database.csv
├── requirements.txt
└── README.md

⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/yourusername/NUTRICALCI.git
cd NUTRICALCI

2️⃣ Create Virtual Environment
python -m venv venv


Activate:

Windows:

venv\Scripts\activate


Mac/Linux:

source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

▶️ Run the Application
streamlit run app.py


App will open at:

http://localhost:8501

📈 How It Works
Nutrition Flow

User Input →
Fetch nutrient data →
Scale by quantity →
Update daily session state →
Tracker analyzes totals →
Display goals and insights

Surplus / Deficit Logic

BMR calculated using simplified Mifflin-St Jeor equation

Maintenance calories adjusted by activity multiplier

Surplus/deficit computed relative to goal

7700 kcal ≈ 1 kg fat (energy balance principle)

🔮 Future Improvements

Weekly tracking graphs

Save daily logs to CSV / database

Food recommendation system

ANN-based nutrient estimation for custom dishes

User authentication system

Cloud deployment (Streamlit Cloud / Docker)

🎯 Why This Project Matters

This project demonstrates:

Clean state management

Practical nutritional calculations

Goal-based tracking

Real-world logic integration

Structured Python architecture

User-focused interface design

It focuses on correctness and clarity over unnecessary complexity.

📜 License

MIT License (or choose your preferred license)

👤 Author

Avinash
Python Developer | ML Enthusiast