# 🌾 कृषिVision
### Intelligent Crop Recommendation and Plant Disease Detection System
**Official Project Name:** **कृषिVision**  
**Tagline:** *Smarter Decisions for Better Farming · Healthier Tomorrow.*  
**Project Category:** B.Tech Computer Science & Engineering Minor Project (7th Semester)

---

## 1. Project Overview & Executive Summary

**कृषिVision** is an AI-powered agricultural decision-support web application designed to help farmers, agronomists, and agricultural extension workers make scientifically sound farming decisions. By integrating multi-parameter soil chemistry, ambient meteorological data, classical machine learning ensembles, and deep foliar vision diagnostics, **कृषिVision** addresses two of the most critical challenges in modern agriculture:

1. **Intelligent Crop Recommendation (Dual-Pathway Architecture):**
   - **Path A (Soil Report Available):** Analyzes 7 critical scientific parameters — Nitrogen ($N$), Phosphorus ($P$), Potassium ($K$), Temperature, Humidity, Soil pH, and Rainfall — using a trained Scikit-Learn **Random Forest Classifier** ($100$ estimators) to recommend a crop among 22 agricultural commodities with predicted-class probability scores, ranking alternatives, and detailed agronomic explanations. These model scores are not empirically calibrated.
   - **Path B (Soil Report NOT Available):** Collects observable farmer-friendly field data (State/Location, Growing Season, Water Availability, Irrigation, Soil Texture, and Previous Crop) and provides rule-based agro-climatic rotations and advisories. It clearly guides the farmer to obtain a formal Soil Health Card without generating misleading synthetic ML scores.

2. **Plant Leaf Disease Detection & Treatment Encyclopedia (Deep Learning Vision):**
   - Employs a **MobileNetV2 Transfer Learning Architecture** trained on foliar leaf images from the benchmark PlantVillage dataset.
   - Accepts leaf photo uploads (drag-and-drop, file selector, or benchmark quick-samples), validates file integrity, and preprocesses foliar inputs to normalized $224 \times 224 \times 3$ RGB tensors.
   - Executes neural inference across **27 agronomic disease and healthy classes** spanning 6 major crop species:
     - **Tomato (10):** Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Two-Spotted Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy.
     - **Potato (3):** Early Blight, Late Blight, Healthy.
     - **Corn / Maize (4):** Cercospora Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy.
     - **Apple (4):** Apple Scab, Black Rot, Cedar Apple Rust, Healthy.
     - **Grape (4):** Black Rot, Esca (Black Measles), Leaf Blight, Healthy.
     - **Bell Pepper (2):** Bacterial Spot, Healthy.
   - Yields predicted plant and disease name, a neural model score (not an empirically calibrated probability), severity rating, foliar symptoms, and **3-Tier Treatment Regimens**:
     - *Tier 1: Organic / Biological Control* (e.g. Neem oil, *Bacillus subtilis*, copper octanoate).
     - *Tier 2: Chemical Fungicide / Bactericide Regimens* (e.g. Mancozeb, Chlorothalonil, Metalaxyl).
     - *Tier 3: Cultural & Preventive Practices* (e.g. Drip irrigation, pruning, crop rotation).

3. **Enterprise-Grade Full-Stack Capabilities:**
   - Relational database persistence powered by **SQLite (WAL mode)** and **SQLAlchemy ORM** for prediction logs, history management, and farmer accounts.
   - Secure token authorization and password hashing using **PBKDF2-HMAC-SHA256**.
   - Interactive analytics aggregating crop distributions, soil averages ($N, P, K, pH$), and health scores.
   - Responsive modern UI styled with **Tailwind CSS**, Google's **Tiro Devanagari Hindi & Inter** typography, and **Lucide Icons**.

---

## 2. Technology Stack & System Architecture

```
                    +-------------------------------------------------------+
                    |             कृषिVision Client Layer                    |
                    |   Tailwind CSS  *  Vanilla JS  *  Lucide Icons       |
                    |   Tiro Devanagari Hindi & Inter Typography            |
                    +---------------------------+---------------------------+
                                                |
                                      HTTP / REST API (JSON)
                                                |
                    +---------------------------v---------------------------+
                    |             FastAPI Backend Layer                     |
                    |   Uvicorn ASGI  *  Pydantic v2  *  CORS Middleware   |
                    +-------------+---------------------------+-------------+
                                  |                           |
             +--------------------+---+           +-----------+--------------------+
             |                        |           |                                |
+------------v------------+ +---------v-------+ +-v----------------+ +-------------v------+
| Scikit-Learn ML Engine  | | Rule Guidance   | | MobileNetV2 DL   | | SQLAlchemy ORM    |
| Random Forest (7 Feat.) | | Agro-Climatic   | | 27 Classes       | | SQLite (WAL Mode) |
| 22 Crop Targets         | | Rotations       | | 224x224x3 Tensor | | Users & Logs      |
+-------------------------+ +-----------------+ +------------------+ +--------------------+
```

| Layer | Technologies Used | Responsibility |
| :--- | :--- | :--- |
| **Frontend UI** | Modern HTML5, JavaScript (ES6+), Tailwind CSS, Lucide Icons | Responsive dashboard, wizard path switcher, charts, drag-and-drop file upload |
| **Backend REST API**| Python 3.10–3.12, FastAPI, Uvicorn, Pydantic v2 | High-throughput asynchronous REST API with auto OpenAPI Swagger docs |
| **Database & ORM** | SQLite (with WAL mode) / PostgreSQL, SQLAlchemy | Relational persistence for user accounts, crop predictions, and disease scans |
| **Security & Auth** | PBKDF2-HMAC-SHA256, Signed Tokens, HTTPBearer | Farmer registration, login/logout, password changes that revoke previous sessions, and protected history records |
| **Crop ML Model** | Scikit-Learn (v1.4+), Joblib, Pandas, NumPy | Random Forest Classifier ($100$ trees, $22$ crops, multi-class probabilities) |
| **Disease Vision** | TensorFlow 2.16+, MobileNetV2, Pillow (PIL), NumPy | 224x224 RGB image normalization, 27-class symptom & treatment catalog |

---

## 3. Official Logo and Brand Identity

The project branding strictly satisfies all design and cultural specifications:
- **Project Name:** **कृषिVision**
  - **कृषि** is written in Hindi (Devanagari script).
  - **Vision** is written in English.
- **Emblem:** A modern green agricultural leaf symbol placed **ABOVE** the project name:
```
              [Green Leaf Symbol]
                   कृषिVision
```
- **Assets Provided:**
  - `frontend/assets/logo.svg` — Primary stacked brand logo (leaf above text).
  - `frontend/assets/logo-horizontal.svg` — Compact horizontal navbar logo.
  - `frontend/assets/favicon.svg` — Browser favicon badge.
  - `frontend/assets/logo.png` — High-resolution transparent PNG.

---

## 4. Machine Learning & Scientific Models

### A. Crop Recommendation Engine (Random Forest)
- **Algorithm:** Random Forest Classifier (`n_estimators=100, random_state=42`)
- **Model File:** `backend/app/ml/crop_recommendation/crop_model.pkl` (7.28 MB)
- **Benchmark Training Set:** 2,200 agricultural samples based on ICAR & Kaggle benchmark distributions.
- **Input Features (7):**
  1. Soil Nitrogen ($N$, 0–140 kg/ha)
  2. Soil Phosphorus ($P$, 5–145 kg/ha)
  3. Soil Potassium ($K$, 5–205 kg/ha)
  4. Ambient Temperature ($T$, 8.0–45.0 °C)
  5. Relative Humidity ($H$, 10.0–100.0 %)
  6. Soil pH ($pH$, 3.5–10.0)
  7. Seasonal Rainfall ($R$, 20.0–300.0 mm)
- **Target Crops (22 Classes):**
  Rice, Maize, Chickpea, Kidneybeans, Pigeonpeas, Mothbeans, Mungbean, Blackgram, Lentil, Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut, Cotton, Jute, Coffee.
- **Top Outputs:** Primary recommended crop, predicted-class probability score (not calibrated), agronomic justification, and top 3 ranking alternatives.

### B. Plant Disease Knowledge Base (MobileNetV2 Deep Learning)
- **Algorithm:** MobileNetV2 Transfer Learning Architecture (ImageNet feature extractor + GlobalAveragePooling2D + Dense 256 + Dropout 0.3 + Softmax Dense 27)
- **Model File:** `backend/app/ml/plant_disease/model/plant_disease_model.keras` (13.06 MB; the trained artifact is already included)
- **Input Tensor:** $224 \times 224 \times 3$ RGB normalized tensor
- **Classes Supported (27 Classes across 6 Species):**
  - *Tomato:* Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Two-Spotted Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy.
  - *Potato:* Early Blight, Late Blight, Healthy.
  - *Corn / Maize:* Cercospora Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy.
  - *Apple:* Apple Scab, Black Rot, Cedar Apple Rust, Healthy.
  - *Grape:* Black Rot, Esca (Black Measles), Leaf Blight, Healthy.
  - *Bell Pepper:* Bacterial Spot, Healthy.
- **Outputs:** Plant species, pathogen taxonomy, severity rating, symptoms, organic controls, chemical fungicides/bactericides, and cultural preventive advice.

---

## 5. REST API Endpoints Overview

Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.

| Method | Endpoint | Access | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Public | Browser: **Landing Page** · API Client: System status JSON |
| `GET` | `/landing` | Public | Official कृषिVision AI Marketing & Product Landing Page |
| `GET` | `/app` | Public | Single-page Agricultural Farmer Portal & Dashboard |
| `GET` | `/api/health` | Public | Database health, model-file status, and cached inference readiness |
| `POST` | `/api/auth/register` | Public | Register new farmer account |
| `POST` | `/api/auth/login` | Public | Authenticate farmer and obtain JWT token |
| `POST` | `/api/auth/logout` | Bearer Token | Revoke the presented access token |
| `GET` | `/api/auth/me` | Bearer Token | Fetch authenticated farmer profile |
| `POST` | `/api/auth/change-password` | Bearer Token | Update account password |
| `GET` | `/api/auth/stats` | Bearer Token | Individual user prediction statistics |
| `POST` | `/api/predict` | Public / Token | **Path A:** Random Forest Crop Recommendation |
| `POST` | `/api/crop-guidance` | Public / Token | **Path B:** Preliminary Agro-Climatic Rule Guidance |
| `GET` | `/api/disease/classes` | Public | List all 27 supported plant disease classes |
| `GET` | `/api/disease/classes/{id}` | Public | Detailed treatments & symptoms for disease ID |
| `POST` | `/api/disease/predict` | Public / Token | **Leaf Image Diagnosis:** Upload foliar photograph |
| `GET` | `/api/history` | Public / Token | Retrieve persisted prediction history |
| `DELETE`| `/api/history/{id}` | Bearer Token | Delete owned prediction record |
| `GET` | `/api/analytics/summary` | Public | Aggregated KPIs, soil averages, and crop trends |

---

## 6. How to Run in Visual Studio Code on Windows

### Prerequisites
- Windows 10 or 11
- Python 3.10, 3.11, or 3.12 (Python 3.12 is already configured in the local `venv`)

### Option A — One-Click Execution (Recommended for Viva Demo)
1. Double-click `start_all.bat` in the project root.
2. The batch script will automatically:
   - Launch the FastAPI server on `http://127.0.0.1:8000`.
   - Open your default web browser to the **कृषिVision Landing Page** (`http://127.0.0.1:8000/`).
   - The interactive Farmer Dashboard is located at `http://127.0.0.1:8000/app`.
   - The Swagger API Docs are at `http://127.0.0.1:8000/docs`.

### Option B — Run Directly inside VS Code
1. Open this `KrishiVision` folder in Visual Studio Code.
2. Press `Ctrl + Shift + P` and choose **Python: Select Interpreter**, then choose `.\venv\Scripts\python.exe`.
3. Press `F5` or go to the **Run & Debug** tab (Ctrl+Shift+D) and select **"🌾 Run KrishiVision Backend (FastAPI)"**.
4. Open your browser and navigate to `http://127.0.0.1:8000/app`.

### Option C — Manual Command Line
```powershell
# 1. Activate Virtual Environment
.\venv\Scripts\activate

# 2. Run Backend Server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --app-dir backend

# Or using the legacy entrypoint:
python backend/app.py
```

### Optional Development Demo Account
Demo login is disabled unless explicitly enabled. To opt in, copy
`backend/.env.example` to `backend/.env`, keep `APP_ENV=development`, set
`DEMO_USER_ENABLED=true`, and supply your own `DEMO_USER_USERNAME`,
`DEMO_USER_EMAIL`, and strong `DEMO_USER_PASSWORD`. Never reuse demo credentials
outside a local development environment. The app creates this account only in
the configured database; the example credentials are placeholders, not usable
login details.

---

## 7. Running the Automated Test Suite

Run the test suite from the repository root. `backend/tests/conftest.py`
redirects database operations to a temporary SQLite file that is removed after
the test session; it does not use `backend/krishivision.db`.

```powershell
.\venv\Scripts\python.exe -m pytest backend\tests -v
```

To run the end-to-end live server verification suite:
```powershell
.\venv\Scripts\python.exe backend\tests\verify_live_server.py
```

The live verification script also creates and removes its own temporary SQLite
database. Read the actual command output for the number of checks and their
results; test totals and timing can change as the suite evolves.

On startup, SQLAlchemy `create_all` may add the two authentication-support
tables (`revoked_access_tokens` and `user_token_invalidations`) to an existing
database. It does not alter or delete existing user rows or other data. Model
health checks do not load model files: a file-only status means inference is
not ready until the model has loaded successfully and is cached by inference.

---

## 8. College Viva Q&A Reference

1. **Why is KrishiVision structured with a Dual-Pathway architecture?**
   - In India, many smallholder farmers do not have a recent Soil Health Card. If a system forces dummy NPK inputs, predictions become meaningless. Path A uses rigorous Random Forest classification when scientific soil tests exist. Path B provides transparent agro-climatic guidance and advises soil testing.
2. **Why Random Forest for Crop Recommendation?**
   - Random Forest is an ensemble of decision trees that handles non-linear agronomic relationships and outputs class probability scores through `predict_proba()`. These scores are not asserted to be empirically calibrated.
3. **Why MobileNetV2 for Plant Disease Detection?**
   - MobileNetV2 uses depthwise separable convolutions and inverted residuals. This project uses it as a transfer-learning backbone; no independent accuracy or latency metrics are reported.
4. **How is security handled?**
   - Passwords are salted and hashed using PBKDF2-HMAC-SHA256 (100,000 iterations). Signed JWTs expire, logout revokes the presented token, and password changes invalidate all prior sessions.
