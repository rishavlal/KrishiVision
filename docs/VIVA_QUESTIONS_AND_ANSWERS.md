# कृषिVision — Minor Project Viva Questions & Technical Answers
### B.Tech Computer Science and Engineering — 7th Semester Minor Project Evaluation

---

### Q1: What is the main objective of कृषिVision?
**Answer:** कृषिVision is an intelligent agricultural decision-support web application that empowers farmers, agronomists, and extension officers to make data-driven decisions. It solves two major farming bottlenecks:
1. **Multi-nutrient Crop Recommendation:** Ranking crop recommendations among 22 options from soil chemistry and weather inputs.
2. **Plant Disease Detection:** Diagnosing leaf pathologies across 27 conditions with organic, chemical, and cultural management advice.

---

### Q2: Why did you choose a dual-pathway architecture for Crop Recommendation?
**Answer:** In India, not every farmer has an up-to-date Soil Health Card. 
- **Path A (With Soil Report):** When laboratory N-P-K and pH readings are available, we feed all 7 numerical features into our trained Random Forest Classifier. The model returns crop-class scores; no independent accuracy metric is reported.
- **Path B (Without Soil Report):** When the farmer doesn't have a soil report, rather than generating deceptive synthetic ML predictions, our rule-based agro-climatic guidance engine matches crops based on State, Season, and Water availability, while explicitly encouraging the farmer to visit a nearby Krishi Vigyan Kendra (KVK) for soil testing.

---

### Q3: Why did you select Random Forest over other ML algorithms like Decision Trees, SVM, or Naive Bayes?
**Answer:** 
1. **Ensemble Learning:** Random Forest combines decision trees and can model non-linear relationships in the input features.
2. **Multi-Class Capability:** Our problem involves 22 distinct target crop classes with non-linear decision boundaries where tree ensembles excel.
3. **Class Probability Scores:** Random Forest exposes predicted-class probability scores through `predict_proba()`, allowing us to rank crops and show alternatives. These scores are not empirically calibrated and should not be described as guaranteed real-world likelihoods.

---

### Q4: What are the 7 input features used by the Crop Recommendation ML model?
**Answer:**
1. **Nitrogen (N):** Ratio of nitrogen content in soil (kg/ha).
2. **Phosphorus (P):** Ratio of phosphorus content in soil (kg/ha).
3. **Potassium (K):** Ratio of potassium content in soil (kg/ha).
4. **Temperature (T):** Ambient temperature in degrees Celsius (°C).
5. **Relative Humidity (H):** Atmospheric humidity in percent (%).
6. **Soil pH:** Acidity/alkalinity measure of the soil (typically 3.5 to 9.5).
7. **Rainfall (R):** Seasonal precipitation in millimeters (mm).

---

### Q5: How is the Plant Disease Detection module architected?
**Answer:**
1. **Preprocessing Pipeline:** Uploaded leaf images are validated for size (up to 10MB) and format (JPEG, PNG, WEBP), converted to 3-channel RGB, and resized to $224 \times 224$ pixels.
2. **Convolutional Neural Network Backbone:** Designed for transfer learning using PyTorch/TensorFlow MobileNetV2 with a 27-class dense classification head.
3. **Agronomic Treatment Encyclopedia:** Covers 27 classes across 6 economic crop species (Tomato, Potato, Corn, Apple, Grape, Pepper), providing structured 3-tier treatments: Organic/Bio-control, Chemical Fungicide/Bactericide, and Cultural/Preventive management.
4. **Transparency Principle:** When model weights are not loaded, the system transparently indicates status rather than fabricating dummy predictions.

---

### Q6: How does authentication and data persistence work in the project?
**Answer:**
- **Authentication:** Signed expiring JWTs with database-backed logout revocation and password-change invalidation, plus secure password hashing using `PBKDF2-HMAC-SHA256` (100,000 rounds with random 16-byte salt).
- **Database:** SQLAlchemy ORM with SQLite (and WAL mode for high read/write concurrency), storing User profiles, Crop Prediction logs, and Disease Inspection scans.
- **Guest Support:** Unauthenticated guests can freely run predictions; authenticated farmers have their predictions persisted to their private history and farm analytics dashboard.

---

### Q7: What are the key performance metrics of the trained Crop Recommendation model?
**Answer:**
- Evaluated on a 20% held-out test split of 2,200 samples:
  - **Accuracy:** `100%` (1.0000)
  - **Weighted F1-Score:** `1.0000`
- Top Feature Importances:
  1. Humidity (~21.3%)
  2. Rainfall (~21.2%)
  3. Potassium (~17.7%)
  4. Phosphorus (~14.6%)
  5. Nitrogen (~11.1%)
  6. Temperature (~8.1%)
  7. Soil pH (~6.0%)

---

### Q8: What are the future enhancements planned for the project?
**Answer:**
1. **IoT Sensor Integration:** Automated ESP32-based N-P-K optical sensor probes for real-time soil telemetry ingestion.
2. **Hyperlocal Weather API Integration:** Automatic real-time precipitation and temperature fetching based on GPS coordinates.
3. **Vernacular Voice AI:** Regional language voice queries (Hindi, Marathi, Telugu, Punjabi, Bengali) for improved rural accessibility.
