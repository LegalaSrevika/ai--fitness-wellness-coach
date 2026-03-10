import React, { useEffect, useMemo, useState } from "react";

const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:5000";

const defaultOptions = {
  genders: ["male", "female"],
  activity_levels: ["sedentary", "light", "moderate", "active", "very_active"],
  goals: ["lose", "maintain", "gain"],
  stress_levels: ["low", "medium", "high"],
  diet_preferences: ["balanced", "vegetarian", "vegan", "high_protein", "keto"],
  equipment_access_options: ["none", "home", "gym"],
};

const initialForm = {
  age: 25,
  gender: "male",
  height: 170,
  weight: 70,
  activity_level: "moderate",
  goal: "maintain",
  sleep_hours: 7,
  stress_level: "medium",
  diet_preference: "balanced",
  workout_days_per_week: 4,
  equipment_access: "home",
  current_water_intake_liters: 2,
};

export default function App() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiStatus, setApiStatus] = useState("checking");
  const [options, setOptions] = useState(defaultOptions);

  const safeOptions = useMemo(() => {
    const merged = { ...defaultOptions, ...(options || {}) };
    return {
      genders: Array.isArray(merged.genders) ? merged.genders : defaultOptions.genders,
      activity_levels: Array.isArray(merged.activity_levels)
        ? merged.activity_levels
        : defaultOptions.activity_levels,
      goals: Array.isArray(merged.goals) ? merged.goals : defaultOptions.goals,
      stress_levels: Array.isArray(merged.stress_levels)
        ? merged.stress_levels
        : defaultOptions.stress_levels,
      diet_preferences: Array.isArray(merged.diet_preferences)
        ? merged.diet_preferences
        : defaultOptions.diet_preferences,
      equipment_access_options: Array.isArray(merged.equipment_access_options)
        ? merged.equipment_access_options
        : defaultOptions.equipment_access_options,
    };
  }, [options]);

  const canSubmit = useMemo(() => {
    const age = Number(form.age);
    const height = Number(form.height);
    const weight = Number(form.weight);
    const sleepHours = Number(form.sleep_hours);
    const workoutDays = Number(form.workout_days_per_week);
    const water = Number(form.current_water_intake_liters);
    return (
      Number.isFinite(age) &&
      Number.isFinite(height) &&
      Number.isFinite(weight) &&
      Number.isFinite(sleepHours) &&
      Number.isFinite(workoutDays) &&
      Number.isFinite(water) &&
      age >= 10 &&
      age <= 100 &&
      height >= 100 &&
      height <= 250 &&
      weight >= 25 &&
      weight <= 300 &&
      sleepHours >= 3 &&
      sleepHours <= 12 &&
      workoutDays >= 1 &&
      workoutDays <= 7 &&
      water >= 0 &&
      water <= 10
    );
  }, [
    form.age,
    form.height,
    form.weight,
    form.sleep_hours,
    form.workout_days_per_week,
    form.current_water_intake_liters,
  ]);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const healthRes = await fetch(`${API_BASE}/api/health`);
        if (!healthRes.ok) {
          setApiStatus("offline");
          return;
        }
        setApiStatus("online");
      } catch {
        setApiStatus("offline");
      }
    };

    const loadOptions = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/options`);
        if (!res.ok) return;
        const data = await res.json();
        setOptions((prev) => ({ ...prev, ...data }));
      } catch {
        // Keep defaults if options endpoint is unavailable.
      }
    };

    checkBackend();
    loadOptions();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!canSubmit) {
      setError("Please provide values in valid ranges before submitting.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data?.error || "Prediction failed.");
        setResult(null);
        return;
      }
      setResult(data);
    } catch {
      setError("Request failed. Make sure backend is running.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handlePrintReport = () => {
    window.print();
  };

  const bmiValue = Number(result?.bmi || 0);
  const bmiPosition = Math.max(0, Math.min(100, ((bmiValue - 10) / 30) * 100));

  return (
    <div className="page">
      <main className="card">
        <div className="header">
          <h1>AI Fitness Coach Pro</h1>
          <span className={`badge ${apiStatus}`}>
            API: {apiStatus === "checking" ? "checking..." : apiStatus}
          </span>
        </div>

        <section className="hero">
          <img
            src="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1400&q=80"
            alt="People training in a gym"
          />
          <div className="hero-overlay">
            <h2>Personalized plan from your daily lifestyle</h2>
            <p>
              Add body stats, sleep, stress, and training preferences to get a
              more practical routine.
            </p>
          </div>
        </section>

        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Age
            <input type="number" name="age" value={form.age} onChange={handleChange} />
          </label>

          <label>
            Gender
            <select name="gender" value={form.gender} onChange={handleChange}>
              {safeOptions.genders.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label>
            Height (cm)
            <input type="number" name="height" value={form.height} onChange={handleChange} />
          </label>

          <label>
            Weight (kg)
            <input type="number" name="weight" value={form.weight} onChange={handleChange} />
          </label>

          <label>
            Activity Level
            <select
              name="activity_level"
              value={form.activity_level}
              onChange={handleChange}
            >
              {safeOptions.activity_levels.map((item) => (
                <option key={item} value={item}>
                  {item.replace("_", " ")}
                </option>
              ))}
            </select>
          </label>

          <label>
            Goal
            <select name="goal" value={form.goal} onChange={handleChange}>
              {safeOptions.goals.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label>
            Sleep Hours
            <input
              type="number"
              step="0.5"
              name="sleep_hours"
              value={form.sleep_hours}
              onChange={handleChange}
            />
          </label>

          <label>
            Stress Level
            <select
              name="stress_level"
              value={form.stress_level}
              onChange={handleChange}
            >
              {safeOptions.stress_levels.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label>
            Diet Preference
            <select
              name="diet_preference"
              value={form.diet_preference}
              onChange={handleChange}
            >
              {safeOptions.diet_preferences.map((item) => (
                <option key={item} value={item}>
                  {item.replace("_", " ")}
                </option>
              ))}
            </select>
          </label>

          <label>
            Workout Days / Week
            <input
              type="number"
              name="workout_days_per_week"
              value={form.workout_days_per_week}
              onChange={handleChange}
            />
          </label>

          <label>
            Equipment Access
            <select
              name="equipment_access"
              value={form.equipment_access}
              onChange={handleChange}
            >
              {safeOptions.equipment_access_options.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label>
            Current Water Intake (L)
            <input
              type="number"
              step="0.1"
              name="current_water_intake_liters"
              value={form.current_water_intake_liters}
              onChange={handleChange}
            />
          </label>

          <button type="submit" disabled={!canSubmit || loading}>
            {loading ? "Calculating..." : "Get Recommendation"}
          </button>
        </form>

        {error && <p className="error">{error}</p>}

        {result && (
          <section className="results" id="fitness-report">
            <h2>Results</h2>
            <p className="report-date">
              Report generated: {new Date().toLocaleString()}
            </p>

            <div className="print-actions no-print">
              <button type="button" onClick={handlePrintReport}>
                Print Report
              </button>
              <button type="button" onClick={handlePrintReport}>
                Download PDF Report
              </button>
            </div>

            <div className="key-metrics">
              <article className="metric-card metric-accent">
                <h3>Recommended Calories</h3>
                <strong>{result.recommended_calories} kcal/day</strong>
              </article>
              <article className="metric-card">
                <h3>BMI Status</h3>
                <strong>
                  {result.bmi} ({result.bmi_status})
                </strong>
              </article>
              <article className="metric-card">
                <h3>Hydration Target</h3>
                <strong>{result.hydration_liters_per_day} L/day</strong>
              </article>
              <article className="metric-card">
                <h3>Hydration Gap</h3>
                <strong>{result.hydration_gap_liters} L to add</strong>
              </article>
            </div>

            <h3>BMI Chart Visualization</h3>
            <div className="bmi-chart">
              <div className="bmi-scale">
                <div className="bmi-segment underweight">Under</div>
                <div className="bmi-segment normal">Normal</div>
                <div className="bmi-segment overweight">Over</div>
                <div className="bmi-segment obese">Obese</div>
                <div className="bmi-marker" style={{ left: `${bmiPosition}%` }} />
              </div>
              <div className="bmi-labels">
                <span>18.5</span>
                <span>25</span>
                <span>30</span>
              </div>
              <p>
                Your BMI: <strong>{result.bmi}</strong> ({result.bmi_status})
              </p>
            </div>

            <h3>Important Highlights</h3>
            <ul className="highlights-list">
              {result.important_highlights?.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>

            <p>
              <strong>Workout Plan:</strong> {result.workout_plan}
            </p>
            <p>
              <strong>Nutrition Tips:</strong> {result.nutrition_tips}
            </p>
            <p>
              <strong>Yoga Recommendation:</strong> {result.yoga_recommendation}
            </p>
            <p>
              <strong>Equipment Tip:</strong> {result.equipment_tip}
            </p>

            <h3>Daily Macro Targets (grams)</h3>
            <p>
              Protein: {result.macro_targets_grams?.protein}g | Carbs:{" "}
              {result.macro_targets_grams?.carbs}g | Fats: {result.macro_targets_grams?.fats}g
            </p>

            <h3>Meal Examples</h3>
            <ul>
              {result.diet_examples?.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>

            <h3>Recovery Tips</h3>
            <ul>
              {result.recovery_tips?.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>

            <h3>7-Day Activity Guide</h3>
            <ul>
              {result.weekly_plan?.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </section>
        )}

        <section className="image-strip">
          <article className="image-tile">
            <img
              src="https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=900&q=80"
              alt="Healthy meal prep containers"
            />
            <span>Consistency in meals</span>
          </article>
          <article className="image-tile">
            <img
              src="https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=900&q=80"
              alt="Strength training workout"
            />
            <span>Progressive training</span>
          </article>
          <article className="image-tile">
            <img
              src="https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?auto=format&fit=crop&w=900&q=80"
              alt="Peaceful sleep and recovery"
            />
            <span>Recovery and sleep</span>
          </article>
        </section>
      </main>
    </div>
  );
}
