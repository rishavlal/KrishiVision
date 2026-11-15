import tensorflow as tf
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"

TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "validation"
TEST_DIR = DATASET_DIR / "test"

# --------------------------------------------------
# Configuration
# --------------------------------------------------
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42

# --------------------------------------------------
# Load datasets
# --------------------------------------------------
print("Loading training dataset...")

train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=True,
    seed=SEED
)

print("\nLoading validation dataset...")

val_ds = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=False
)

print("\nLoading test dataset...")

test_ds = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=False
)

# --------------------------------------------------
# Class information
# --------------------------------------------------
class_names = train_ds.class_names

print("\nNumber of classes:", len(class_names))
print("\nFirst 10 classes:")
for i, name in enumerate(class_names[:10]):
    print(f"{i}: {name}")

# --------------------------------------------------
# MobileNetV2 preprocessing
# --------------------------------------------------
preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input

def preprocess_images(images, labels):
    images = tf.cast(images, tf.float32)
    images = preprocess_input(images)
    return images, labels

train_processed = train_ds.map(
    preprocess_images,
    num_parallel_calls=tf.data.AUTOTUNE
)

# --------------------------------------------------
# Inspect one batch
# --------------------------------------------------
print("\nInspecting one training batch...")

images, labels = next(iter(train_processed))

print("Image batch shape:", images.shape)
print("Label batch shape:", labels.shape)
print("Image dtype:", images.dtype)

print("Minimum pixel value:", tf.reduce_min(images).numpy())
print("Maximum pixel value:", tf.reduce_max(images).numpy())

print("Minimum label:", tf.reduce_min(labels).numpy())
print("Maximum label:", tf.reduce_max(labels).numpy())

# --------------------------------------------------
# Final checks
# --------------------------------------------------
print("\nFINAL CHECKS")

if len(class_names) != 38:
    print("❌ Expected 38 classes, but found:", len(class_names))
else:
    print("✅ Correct number of classes: 38")

if images.shape[1:] == (224, 224, 3):
    print("✅ Image shape is correct: (224, 224, 3)")
else:
    print("❌ Unexpected image shape:", images.shape[1:])

if labels.shape[0] == images.shape[0]:
    print("✅ Number of images and labels match")
else:
    print("❌ Image/label count mismatch")

if images.dtype == tf.float32:
    print("✅ Image dtype is float32")
else:
    print("❌ Unexpected image dtype:", images.dtype)

if -1.1 <= float(tf.reduce_min(images).numpy()) <= 1.1:
    print("✅ MobileNetV2 preprocessing appears correct")
else:
    print("⚠️ Check preprocessing range")

if 0 <= int(tf.reduce_min(labels).numpy()) <= 37 and \
   0 <= int(tf.reduce_max(labels).numpy()) <= 37:
    print("✅ Labels are within expected range: 0–37")
else:
    print("❌ Unexpected label range")

print("\nData loader test completed.")