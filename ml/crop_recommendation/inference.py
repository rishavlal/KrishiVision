import os
import joblib
import pandas as pd


# Get the folder containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to trained model
MODEL_PATH = os.path.join(BASE_DIR, "crop_model.pkl")

# Feature order used during model training
FEATURES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
]


# Load trained model
model = joblib.load(MODEL_PATH)


def predict_crop(
    nitrogen,
    phosphorus,
    potassium,
    temperature,
    humidity,
    ph,
    rainfall
):
    """
    Predict the recommended crop using the trained Random Forest model.
    """

    input_data = pd.DataFrame([{
        "N": nitrogen,
        "P": phosphorus,
        "K": potassium,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall
    }])

    # Keep the exact feature order used during training
    input_data = input_data[FEATURES]

    # Predict crop
    prediction = model.predict(input_data)[0]

    # Get probability for each crop
    probabilities = model.predict_proba(input_data)[0]

    # Highest predicted probability
    confidence = probabilities.max() * 100

    return {
        "crop": prediction,
        "confidence": round(float(confidence), 2)
    }