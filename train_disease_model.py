"""
KrishiVision AI - Plant Disease Neural Model Training Pipeline
==============================================================
Trains a MobileNetV2 Transfer Learning classifier on the PlantVillage dataset
stored in ml/plant_disease/dataset.zip across the 27 agricultural disease classes.
Saves the genuine trained model artifact to backend/app/ml/plant_disease/model/plant_disease_model.keras.
"""

import os
import io
import json
import zipfile
import numpy as np
from pathlib import Path
from PIL import Image

# Suppress TF verbose logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # CPU training

import tensorflow as tf
from tensorflow.keras import layers, models, optimizers

# Define paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR
ZIP_PATH = PROJECT_ROOT / "ml" / "plant_disease" / "dataset.zip"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "app" / "ml" / "plant_disease" / "model"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_SAVE_PATH = OUTPUT_DIR / "plant_disease_model.keras"
CLASS_NAMES_PATH = OUTPUT_DIR / "class_names.json"

# Import disease catalog to verify exact 27 classes
import sys
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
from app.ml.plant_disease.disease_catalog import DISEASE_CATALOG

CLASSES = sorted(list(DISEASE_CATALOG.keys()))
NUM_CLASSES = len(CLASSES)
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
TRAIN_PER_CLASS = 40
VAL_PER_CLASS = 10
SEED = 42

print(f"Target Classes ({NUM_CLASSES}):")
for idx, cls in enumerate(CLASSES):
    print(f"  [{idx:02d}] {cls}")

print("\nExtracting and preparing balanced dataset from dataset.zip...")
np.random.seed(SEED)

x_train, y_train = [], []
x_val, y_val = [], []

with zipfile.ZipFile(ZIP_PATH, 'r') as z:
    all_names = z.namelist()
    for cls_idx, cls_name in enumerate(CLASSES):
        # Look in train folder
        prefix = f"dataset/train/{cls_name}/"
        class_files = [f for f in all_names if f.startswith(prefix) and not f.endswith('/')]
        
        # If train didn't have enough, check validation or test
        if len(class_files) < (TRAIN_PER_CLASS + VAL_PER_CLASS):
            val_prefix = f"dataset/validation/{cls_name}/"
            class_files += [f for f in all_names if f.startswith(val_prefix) and not f.endswith('/')]
            test_prefix = f"dataset/test/{cls_name}/"
            class_files += [f for f in all_names if f.startswith(test_prefix) and not f.endswith('/')]
        
        np.random.shuffle(class_files)
        selected_train = class_files[:TRAIN_PER_CLASS]
        selected_val = class_files[TRAIN_PER_CLASS : TRAIN_PER_CLASS + VAL_PER_CLASS]
        
        for fpath in selected_train:
            try:
                img_data = z.read(fpath)
                img = Image.open(io.BytesIO(img_data)).convert("RGB").resize(IMG_SIZE, Image.Resampling.BILINEAR)
                x_train.append(np.array(img, dtype=np.float32))
                y_train.append(cls_idx)
            except Exception as e:
                print(f"Error loading {fpath}: {e}")
                
        for fpath in selected_val:
            try:
                img_data = z.read(fpath)
                img = Image.open(io.BytesIO(img_data)).convert("RGB").resize(IMG_SIZE, Image.Resampling.BILINEAR)
                x_val.append(np.array(img, dtype=np.float32))
                y_val.append(cls_idx)
            except Exception as e:
                print(f"Error loading {fpath}: {e}")

x_train = np.array(x_train, dtype=np.float32)
y_train = np.array(y_train, dtype=np.int32)
x_val = np.array(x_val, dtype=np.float32)
y_val = np.array(y_val, dtype=np.int32)

print(f"\nDataset loaded:")
print(f"  Training samples: {len(x_train)} (shape: {x_train.shape})")
print(f"  Validation samples: {len(x_val)} (shape: {x_val.shape})")

# MobileNetV2 preprocessing: scales pixel values to [-1, 1]
x_train = tf.keras.applications.mobilenet_v2.preprocess_input(x_train)
x_val = tf.keras.applications.mobilenet_v2.preprocess_input(x_val)

print("\nBuilding MobileNetV2 Transfer Learning Architecture...")
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)
base_model.trainable = False  # Freeze base feature extractor

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    layers.Dense(256, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(NUM_CLASSES, activation="softmax")
])

model.compile(
    optimizer=optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

print(model.summary())

print("\nTraining MobileNetV2 classifier...")
epochs = 5
history = model.fit(
    x_train, y_train,
    validation_data=(x_val, y_val),
    epochs=epochs,
    batch_size=BATCH_SIZE,
    verbose=1
)

print("\nSaving trained model and class labels...")
model.save(str(MODEL_SAVE_PATH))
print(f"Model saved to: {MODEL_SAVE_PATH} ({MODEL_SAVE_PATH.stat().st_size / (1024*1024):.2f} MB)")

# Also copy to root ml folder for redundancy
root_ml_dir = PROJECT_ROOT / "ml" / "plant_disease" / "model"
root_ml_dir.mkdir(parents=True, exist_ok=True)
import shutil
shutil.copy2(str(MODEL_SAVE_PATH), str(root_ml_dir / "plant_disease_model.keras"))

with open(CLASS_NAMES_PATH, "w", encoding="utf-8") as f:
    json.dump(CLASSES, f, indent=2)
shutil.copy2(str(CLASS_NAMES_PATH), str(root_ml_dir / "class_names.json"))
print(f"Class names mapping saved to: {CLASS_NAMES_PATH}")

# Quick verification test on a sample
print("\nVerifying inference on a validation leaf image...")
sample_img = x_val[0:1]
preds = model.predict(sample_img)
pred_idx = np.argmax(preds[0])
confidence = float(np.max(preds[0])) * 100
true_cls = CLASSES[y_val[0]]
pred_cls = CLASSES[pred_idx]

print(f"True Class:      {true_cls}")
print(f"Predicted Class: {pred_cls}")
print(f"Confidence:      {confidence:.2f}%")
print("\nPlant Disease Model training and validation completed successfully!")
