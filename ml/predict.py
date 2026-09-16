import joblib
from pathlib import Path
import pandas as pd

def predict_test_risk(duration_sec: float):
    model_path = "ml/models/test_failure_model.pkl"
    print(f"Checking for model at: {model_path}")
    
    if not Path(model_path).exists():
        print("ERROR: Model file not found. Please run 'python ml/train_model.py' first.")
        return

    # Load the trained XGBoost model
    print("Loading model...")
    model = joblib.load(model_path)
    
    # Prepare input data
    input_data = pd.DataFrame([[duration_sec]], columns=['execution_duration_sec'])
    
    # Predict
    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1] # Probability of failure
    
    print("\n--- AI Test Failure Prediction Result ---")
    print(f"Test Execution Duration: {duration_sec} seconds")
    if prediction == 1:
        print(f"Prediction: ⚠️ HIGH RISK OF FAILURE (Failure Probability: {probability * 100:.2f}%)")
    else:
        print(f"Prediction: ✅ LOW RISK / LIKELY TO PASS (Failure Probability: {probability * 100:.2f}%)")

if __name__ == "__main__":
    predict_test_risk(25.5)