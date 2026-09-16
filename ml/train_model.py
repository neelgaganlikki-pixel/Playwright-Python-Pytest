import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import joblib
from pathlib import Path

def train_model():
    data_path = "ml/historical_test_data.csv"
    print(f"Looking for dataset at: {data_path}")
    
    if not Path(data_path).exists():
        print("ERROR: Dataset not found. Run parse_results.py first.")
        return

    df = pd.read_csv(data_path)
    print(f"Loaded dataset with {len(df)} rows.")
    
    X = df[['execution_duration_sec']]
    y = df['test_failed']
    
    if len(df) < 2:
        print("ERROR: Not enough samples to train.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training XGBoost model...")
    model = XGBClassifier(n_estimators=50, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    
    Path("ml/models").mkdir(parents=True, exist_ok=True)
    model_path = "ml/models/test_failure_model.pkl"
    joblib.dump(model, model_path)
    print(f"SUCCESS: Model trained and saved to {model_path}")

if __name__ == "__main__":
    train_model()