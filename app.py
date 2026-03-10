from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

VALID_GENDERS = {"male", "female"}
VALID_ACTIVITY_LEVELS = {"sedentary", "light", "moderate", "active", "very_active"}
VALID_GOALS = {"lose", "maintain", "gain"}
VALID_STRESS_LEVELS = {"low", "medium", "high"}
VALID_DIET_PREFERENCES = {"balanced", "vegetarian", "vegan", "high_protein", "keto"}
VALID_EQUIPMENT = {"none", "home", "gym"}

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def _build_error(message, status=400):
    return jsonify({"error": message}), status


def _validate_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Invalid JSON body. Send a JSON object.")

    required_fields = [
        "age",
        "height",
        "weight",
        "gender",
        "activity_level",
        "goal",
        "sleep_hours",
        "stress_level",
        "diet_preference",
        "workout_days_per_week",
        "equipment_access",
    ]
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")

    try:
        age = int(payload["age"])
        height = float(payload["height"])
        weight = float(payload["weight"])
        sleep_hours = float(payload["sleep_hours"])
        workout_days_per_week = int(payload["workout_days_per_week"])
    except (TypeError, ValueError):
        raise ValueError(
            "Age, height, weight, sleep hours, and workout days must be numeric values."
        )

    if age < 10 or age > 100:
        raise ValueError("Age must be between 10 and 100.")
    if height < 100 or height > 250:
        raise ValueError("Height must be between 100 and 250 cm.")
    if weight < 25 or weight > 300:
        raise ValueError("Weight must be between 25 and 300 kg.")
    if sleep_hours < 3 or sleep_hours > 12:
        raise ValueError("Sleep hours must be between 3 and 12.")
    if workout_days_per_week < 1 or workout_days_per_week > 7:
        raise ValueError("Workout days per week must be between 1 and 7.")

    gender = str(payload["gender"]).lower().strip()
    activity_level = str(payload["activity_level"]).lower().strip()
    goal = str(payload["goal"]).lower().strip()
    stress_level = str(payload["stress_level"]).lower().strip()
    diet_preference = str(payload["diet_preference"]).lower().strip()
    equipment_access = str(payload["equipment_access"]).lower().strip()

    if gender not in VALID_GENDERS:
        raise ValueError(f"Gender must be one of: {', '.join(sorted(VALID_GENDERS))}")
    if activity_level not in VALID_ACTIVITY_LEVELS:
        raise ValueError(
            "Activity level must be one of: "
            + ", ".join(sorted(VALID_ACTIVITY_LEVELS))
        )
    if goal not in VALID_GOALS:
        raise ValueError(f"Goal must be one of: {', '.join(sorted(VALID_GOALS))}")
    if stress_level not in VALID_STRESS_LEVELS:
        raise ValueError(
            f"Stress level must be one of: {', '.join(sorted(VALID_STRESS_LEVELS))}"
        )
    if diet_preference not in VALID_DIET_PREFERENCES:
        raise ValueError(
            "Diet preference must be one of: "
            + ", ".join(sorted(VALID_DIET_PREFERENCES))
        )
    if equipment_access not in VALID_EQUIPMENT:
        raise ValueError(
            f"Equipment access must be one of: {', '.join(sorted(VALID_EQUIPMENT))}"
        )

    current_water_intake_liters = payload.get("current_water_intake_liters", 2)
    try:
        current_water_intake_liters = float(current_water_intake_liters)
    except (TypeError, ValueError):
        raise ValueError("Current water intake must be numeric.")

    if current_water_intake_liters < 0 or current_water_intake_liters > 10:
        raise ValueError("Current water intake must be between 0 and 10 liters.")

    return {
        "age": age,
        "height": height,
        "weight": weight,
        "gender": gender,
        "activity_level": activity_level,
        "goal": goal,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "diet_preference": diet_preference,
        "workout_days_per_week": workout_days_per_week,
        "equipment_access": equipment_access,
        "current_water_intake_liters": current_water_intake_liters,
    }


def _get_bmi_status(bmi):
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def _get_goal_content(goal):
    if goal == "lose":
        return {
            "calorie_adjustment": -450,
            "workout": "4-day split: cardio intervals, full-body strength, and brisk walks.",
            "nutrition": "Prioritize protein, fiber, and whole foods while reducing added sugars.",
            "yoga": "20-30 min Vinyasa or flow yoga for recovery and mobility.",
            "macro_split": {"protein_percent": 35, "carbs_percent": 35, "fats_percent": 30},
            "weekly_plan": [
                "Mon: 30 min brisk walk + core",
                "Tue: Strength training (upper body)",
                "Wed: Light yoga + mobility",
                "Thu: Strength training (lower body)",
                "Fri: Cardio intervals 20-25 min",
                "Sat: Full body circuit",
                "Sun: Rest + stretching",
            ],
        }

    if goal == "gain":
        return {
            "calorie_adjustment": 350,
            "workout": "Progressive overload with compound lifts 4-5 days/week.",
            "nutrition": "Eat a steady caloric surplus with quality carbs, protein, and fats.",
            "yoga": "15-20 min Hatha yoga for flexibility and recovery.",
            "macro_split": {"protein_percent": 30, "carbs_percent": 45, "fats_percent": 25},
            "weekly_plan": [
                "Mon: Push day + light stretching",
                "Tue: Pull day",
                "Wed: Legs day",
                "Thu: Active recovery walk",
                "Fri: Push day (progressive overload)",
                "Sat: Pull + posterior chain",
                "Sun: Mobility + rest",
            ],
        }

    return {
        "calorie_adjustment": 0,
        "workout": "Balanced mix of strength, cardio, and mobility 4 days/week.",
        "nutrition": "Maintain balanced meals with protein, carbs, fats, and vegetables.",
        "yoga": "15-20 min daily mindful yoga or Surya Namaskar.",
        "macro_split": {"protein_percent": 30, "carbs_percent": 40, "fats_percent": 30},
        "weekly_plan": [
            "Mon: Full-body strength",
            "Tue: Light cardio + stretching",
            "Wed: Core + mobility",
            "Thu: Full-body strength",
            "Fri: Moderate cardio",
            "Sat: Yoga or sports activity",
            "Sun: Recovery walk",
        ],
    }


def _diet_examples(diet_preference):
    samples = {
        "balanced": [
            "Breakfast: oats + fruit + eggs",
            "Lunch: rice + dal + vegetables + salad",
            "Dinner: grilled protein + quinoa + greens",
        ],
        "vegetarian": [
            "Breakfast: greek yogurt + nuts + berries",
            "Lunch: paneer/chickpea bowl + salad",
            "Dinner: lentil soup + whole grain roti + veggies",
        ],
        "vegan": [
            "Breakfast: tofu scramble + whole grain toast",
            "Lunch: quinoa + beans + avocado bowl",
            "Dinner: tempeh stir fry + brown rice",
        ],
        "high_protein": [
            "Breakfast: eggs/egg-white omelet + oats",
            "Lunch: chicken/fish + sweet potato + salad",
            "Dinner: lean protein + vegetables + yogurt",
        ],
        "keto": [
            "Breakfast: omelet + avocado",
            "Lunch: grilled paneer/chicken + leafy greens",
            "Dinner: salmon/tofu + sauteed vegetables",
        ],
    }
    return samples.get(diet_preference, samples["balanced"])


def _equipment_tip(equipment_access):
    if equipment_access == "gym":
        return "Use compound lifts (squat, bench, rows, deadlift) for efficient progress."
    if equipment_access == "home":
        return "Use resistance bands and dumbbells. Track reps weekly for progressive overload."
    return "Prioritize bodyweight circuits, walking, stairs, and mobility sessions."


def _stress_recovery_tip(stress_level, sleep_hours):
    tips = []
    if stress_level == "high":
        tips.append("High stress detected: add 10 min breathing or meditation after workouts.")
    elif stress_level == "medium":
        tips.append("Moderate stress: keep at least 1 full recovery day weekly.")
    else:
        tips.append("Low stress: you can safely maintain training intensity progression.")

    if sleep_hours < 6.5:
        tips.append("Sleep is low. Prioritize 7-8 hours to improve recovery and hormonal balance.")
    else:
        tips.append("Sleep looks decent. Maintain a consistent bedtime schedule.")

    return tips


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "ai-fitness-coach-backend"}), 200


@app.route("/api/options", methods=["GET"])
def options():
    return (
        jsonify(
            {
                "genders": sorted(VALID_GENDERS),
                "activity_levels": sorted(VALID_ACTIVITY_LEVELS),
                "goals": sorted(VALID_GOALS),
                "stress_levels": sorted(VALID_STRESS_LEVELS),
                "diet_preferences": sorted(VALID_DIET_PREFERENCES),
                "equipment_access_options": sorted(VALID_EQUIPMENT),
            }
        ),
        200,
    )


@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True)
        profile = _validate_payload(data)
        age = profile["age"]
        height = profile["height"]
        weight = profile["weight"]
        gender = profile["gender"]
        activity_level = profile["activity_level"]
        goal = profile["goal"]

        height_m = height / 100
        bmi = round(weight / (height_m**2), 2)
        bmi_status = _get_bmi_status(bmi)

        if gender == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        base_tdee = bmr * ACTIVITY_FACTORS[activity_level]
        goal_content = _get_goal_content(goal)
        recovery_adjustment = 0
        if profile["sleep_hours"] < 6:
            recovery_adjustment -= 100
        if profile["stress_level"] == "high":
            recovery_adjustment -= 80

        recommended_calories = max(
            1200,
            round(base_tdee + goal_content["calorie_adjustment"] + recovery_adjustment),
        )

        protein_grams = round(
            (recommended_calories * goal_content["macro_split"]["protein_percent"] / 100)
            / 4
        )
        carbs_grams = round(
            (recommended_calories * goal_content["macro_split"]["carbs_percent"] / 100)
            / 4
        )
        fats_grams = round(
            (recommended_calories * goal_content["macro_split"]["fats_percent"] / 100) / 9
        )
        water_liters = round(weight * 0.033, 1)
        hydration_gap = round(max(0, water_liters - profile["current_water_intake_liters"]), 1)

        important_highlights = [
            f"Daily calorie target: {recommended_calories} kcal",
            f"Target protein: {protein_grams}g/day",
            f"Hydration target: {water_liters}L/day",
        ]
        if bmi_status in {"Overweight", "Obese"}:
            important_highlights.append("Focus on steady fat loss: 0.3 to 0.6 kg per week.")
        if profile["sleep_hours"] < 6.5:
            important_highlights.append("Improve sleep quality first to unlock better fitness results.")

        response = {
            "message": "Prediction generated successfully.",
            "input": profile,
            "bmi": bmi,
            "bmi_status": bmi_status,
            "bmr": round(bmr),
            "maintenance_calories": round(base_tdee),
            "recommended_calories": recommended_calories,
            "workout_plan": goal_content["workout"],
            "nutrition_tips": goal_content["nutrition"],
            "yoga_recommendation": goal_content["yoga"],
            "hydration_liters_per_day": water_liters,
            "macro_targets_grams": {
                "protein": protein_grams,
                "carbs": carbs_grams,
                "fats": fats_grams,
            },
            "weekly_plan": goal_content["weekly_plan"],
            "diet_examples": _diet_examples(profile["diet_preference"]),
            "equipment_tip": _equipment_tip(profile["equipment_access"]),
            "recovery_tips": _stress_recovery_tip(
                profile["stress_level"], profile["sleep_hours"]
            ),
            "hydration_gap_liters": hydration_gap,
            "important_highlights": important_highlights,
        }

        return jsonify(response), 200
    except ValueError as exc:
        return _build_error(str(exc), status=400)
    except Exception:
        return _build_error("Unexpected server error.", status=500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
