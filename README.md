# 🥗 NutriCalci Pro  
### Intelligent Nutrition Calculator (Python + Streamlit)

NutriCalci Pro is a Python-based nutrition tracking system designed to calculate, track, and analyze daily food intake using real nutritional logic and structured architecture.

The system focuses on correctness, clarity, and practical usability rather than unnecessary complexity.

---

## 🔗 Live Application

🌐 https://nutricalcipro.streamlit.app/

---

## 🚀 Core Features

---

### 🥗 Nutrition Calculator

- Select food from dataset  
- Enter quantity and servings  
- Automatically calculates:
  - Calories  
  - Protein  
  - Carbohydrates  
  - Fat  
  - Fiber  
  - Sugar  
  - Sodium  
- Displays macro distribution chart  

---

### 🍲 Custom Recipe Builder

- Select multiple ingredients  
- Enter quantity for each  
- Calculates total recipe nutrition  
- Combined macro breakdown  

---

### 📈 Daily Tracker

- Tracks total daily calories  
- Tracks protein, carbs, and fat  
- Displays calorie goal progress  
- Displays protein goal progress  
- Shows macro percentage breakdown:
  - % Calories from Carbs  
  - % from Protein  
  - % from Fat  

---

### ⚖️ Surplus / Deficit Calculator

User selects goal:
- Maintain  
- Weight Loss  
- Weight Gain  

Calculates:
- Estimated maintenance calories  
- Recommended target calories  
- Surplus / deficit amount  

Based on:
- Simplified Mifflin-St Jeor BMR equation  
- Activity multiplier logic  
- 7700 kcal ≈ 1 kg fat principle  

---

### 🧍 BMI Calculator

- Enter weight and height  
- Calculates BMI  
- Displays health classification  

---

## 🧠 Tech Stack

### 💻 Core Language
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

### 🚀 Framework
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

### 📊 Data Handling
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)

### 🔮 Future Expansion
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)

---

## 📊 Dataset

The application uses a cleaned nutrition dataset (`database.csv`) containing:

- Dish Name  
- Calories  
- Protein  
- Carbohydrates  
- Fat  
- Fiber  
- Micronutrients  

All values standardized per 100 grams.

---

## 📁 Project Structure

NUTRICALCI/
│
├── app.py
├── database.csv
├── requirements.txt
└── README.md


---

## ⚙️ Installation & Setup

### 📥 Clone Repository

```bash
git clone https://github.com/yourusername/NUTRICALCI.git
cd NUTRICALCI

🧪 Create Virtual Environment
python -m venv venv


Activate:

Windows

venv\Scripts\activate


macOS / Linux

source venv/bin/activate

📦 Install Dependencies
pip install -r requirements.txt

▶️ Run the Application
streamlit run app.py

📈 System Logic Flow
Nutrition Flow

User Input →
Fetch nutrient data →
Scale by quantity →
Update session state →
Analyze totals →
Display goals & insights

Energy Balance Logic

BMR calculated using simplified Mifflin-St Jeor equation

Maintenance calories adjusted via activity multiplier

Surplus / deficit computed relative to goal

7700 kcal ≈ 1 kg fat

🔮 Future Improvements

Weekly tracking graphs

Save logs to CSV / database

Food recommendation system

ANN-based custom dish nutrient estimation

User authentication

Docker / cloud deployment
