import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Train a simple model from dataset.csv and save model + encoders
data = pd.read_csv("dataset.csv")

le_gender = LabelEncoder()
le_activity = LabelEncoder()
le_goal = LabelEncoder()
le_exercise = LabelEncoder()

data["gender"] = le_gender.fit_transform(data["gender"])
data["activity_level"] = le_activity.fit_transform(data["activity_level"])
data["goal"] = le_goal.fit_transform(data["goal"])

X = data[["age", "gender", "height", "weight", "activity_level", "goal"]]
y = le_exercise.fit_transform(data["recommended_exercise"])

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

joblib.dump(model, "fitness_model.pkl")
joblib.dump((le_gender, le_activity, le_goal, le_exercise), "encoders.pkl")

print("Model and encoders saved to fitness_model.pkl and encoders.pkl")
