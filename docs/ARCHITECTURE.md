# कृषिVision — System Architecture & Engineering Design

```
+-----------------------------------------------------------------------------------+
|                                 USER INTERFACE                                    |
|   Tailwind CSS · Lucide Icons · Tiro Devanagari Hindi · Responsive HTML5 SPA      |
+-----------------------------------------------------------------------------------+
        |                                       ^
        | HTTP Requests (REST / JSON / Multipart)| JSON Responses
        v                                       |
+-----------------------------------------------------------------------------------+
|                              FASTAPI REST API SERVER                              |
|                                                                                   |
|  +-------------------+  +--------------------+  +-------------------------------+ |
|  | /api/auth/*       |  | /api/predict       |  | /api/disease/*                | |
|  | (JWT Auth)        |  | /api/crop-guidance |  | (Upload, Preprocessing, Cat)  | |
|  +-------------------+  +--------------------+  +-------------------------------+ |
|  +-------------------+  +-------------------------------------------------------+ |
|  | /api/history/*    |  | /api/analytics/summary                                | |
|  +-------------------+  +-------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
        |                                                              |
        v                                                              v
+-------------------------------+              +------------------------------------+
|     DATABASE & PERSISTENCE    |              |       MACHINE LEARNING ENGINES     |
|  SQLAlchemy ORM · SQLite DB   |              |                                    |
|  - Users                      |              |  [PATH A: Crop Recommendation]     |
|  - Crop Predictions           |              |  - Random Forest Classifier       |
|  - Disease Predictions        |              |  - 7 Soil & Meteorological Inputs  |
|  - Revoked Access Tokens      |              |  - crop_model.pkl (22 Classes)    |
|  - User Token Invalidations   |              |                                    |
|                               |              |  - crop_model.pkl (22 Classes)     |
+-------------------------------+              |                                    |
                                               |  [PATH B: Preliminary Guidance]    |
                                               |  - Agro-Climatic Rule Engine       |
                                               |  - State / Season / Water Matching |
                                               |                                    |
                                               |  [PLANT DISEASE VISION ENGINE]     |
                                               |  - 224x224 RGB Normalization       |
                                               |  - 27-Class Treatment Encyclopedia |
                                               +------------------------------------+
```

## Directory Responsibilities

- **`backend/app/main.py`**: Application bootstrap, CORS middleware, router registration, lifespan startup seeding.
- **`backend/app/core/`**: Central application configurations, signed JWT handling, persisted logout revocation and password-change invalidation, PBKDF2 password hashing.
- **`backend/app/db/`**: SQLAlchemy database connection, session dependency, relational entity models, and additive token-revocation tables.
- **`backend/app/schemas/`**: Pydantic v2 data transfer schemas for request validation and serialisation.
- **`backend/app/api/`**: API endpoints segmented into modular routers: auth, crop, disease, history, analytics.
- **`backend/app/ml/crop_recommendation/`**: Preserved Random Forest model `crop_model.pkl`, inference pipeline, guidance engine, reference CSV.
- **`backend/app/ml/plant_disease/`**: Preprocessing pipeline, 27-class symptom and treatment catalog.
- **`/api/health`**: Reports database connectivity, model-file presence, and cached inference readiness without loading models during health requests.
- **`frontend/`**: Single-page web dashboard, interactive wizard for Path A and Path B, drag-and-drop foliar upload, history table, and analytics charts.
- **`frontend/assets/`**: Brand assets featuring the green leaf emblem above the **कृषिVision** project name.
