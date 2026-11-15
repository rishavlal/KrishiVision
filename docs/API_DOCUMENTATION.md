# कृषिVision — Complete REST API Documentation

This document provides request payloads, response structures, and sample usage for all **कृषिVision** backend endpoints.

Interactive Swagger UI is also accessible at: `http://127.0.0.1:8000/docs`

---

## 1. System Endpoints

### `GET /`
Returns system status, title, version, and route index.
- **Access:** Public
- **Response `200 OK`:**
```json
{
  "service": "कृषिVision AI API",
  "official_title": "कृषिVision – Intelligent Crop Recommendation and Plant Disease Detection System",
  "version": "1.0.0",
  "status": "online",
  "documentation": "/docs"
}
```

### `GET /api/health`
Reports database connectivity, model-file availability, and cached inference readiness without loading models.
- **Access:** Public
- **Response `200 OK`:**
```json
{
  "status": "degraded",
  "ready": false,
  "readiness": "not_ready",
  "timestamp": "2026-11-01T15:00:00Z",
  "services": {
    "database": "connected",
    "crop_recommendation_ml_model": "file_available",
    "crop_recommendation_model_file_available": true,
    "crop_recommendation_model_loaded": false,
    "crop_recommendation_model_ready": false,
    "crop_guidance_rule_engine": "active",
    "plant_disease_model": "file_available",
    "plant_disease_model_file_available": true,
    "plant_disease_model_loaded": false,
    "plant_disease_model_ready": false,
    "plant_disease_catalog": "active (27 classes)",
    "authentication": "jwt_active"
  }
}
```
`loaded` means the model is cached after successful loading; `file_available`
only confirms that a model file exists and is not inference-ready. Health
requests never load the large models. Readiness becomes true after both models
have loaded and the database is connected.

---

## 2. Authentication Endpoints

### `POST /api/auth/register`
Creates a new farmer profile and returns an access token.
- **Request Body:**
```json
{
  "username": "farmer_anil",
  "email": "anil@farm.in",
  "password": "SecretPassword123",
  "full_name": "Anil Kumar",
  "farm_location": "Patna, Bihar",
  "farm_size_hectares": 3.0,
  "phone_number": "+91 9876543210"
}
```
- **Response `201 Created`:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "username": "farmer_anil",
    "email": "anil@farm.in",
    "full_name": "Anil Kumar",
    "farm_location": "Patna, Bihar",
    "farm_size_hectares": 3.0,
    "phone_number": "+91 9876543210",
    "created_at": "2026-11-01T15:00:00"
  }
}
```

### `POST /api/auth/login`
Authenticates existing farmer credentials.
- **Request Body:**
```json
{
  "username": "your-registered-username",
  "password": "your-password"
}
```
For local development, an optional demo account can be configured through
`backend/.env` as described in the README.

### `POST /api/auth/logout`
Revokes the presented bearer token in the database.
- **Headers:** `Authorization: Bearer <access_token>`
- **Response `200 OK`:** `{"status": "success", "message": "Access token revoked."}`

### `GET /api/auth/me`
Fetches current user's authenticated profile.
- **Headers:** `Authorization: Bearer <access_token>`

### `POST /api/auth/change-password`
Changes the password after verifying the current password and invalidates every
pre-change access token, including the token used for this request. Sign in
again with the new password to obtain a new session.

The revocation state is stored in additive database tables created by the
existing SQLAlchemy `create_all` startup step. Existing user rows are not
rewritten; older signed tokens without an issuance timestamp continue to work
until expiry unless logout revokes them or a password change invalidates prior
sessions.

---

## 3. Crop Recommendation Endpoints

### `POST /api/predict` (Path A: Soil Report Available)
Runs the trained Random Forest model on 7 soil and meteorological inputs.
- The legacy JSON field `confidence` is the predicted-class probability score
  from `predict_proba()`. It is not empirically calibrated and should not be
  interpreted as a guaranteed real-world likelihood.
- **Request Body:**
```json
{
  "nitrogen": 85.0,
  "phosphorus": 45.0,
  "potassium": 40.0,
  "temperature": 27.5,
  "humidity": 75.0,
  "ph": 6.5,
  "rainfall": 200.0,
  "location": "Ranchi, Jharkhand",
  "season": "Kharif",
  "soil_type": "Loamy"
}
```
- **Response `200 OK`:**
```json
{
  "crop": "Rice",
  "confidence": 94.5,
  "description": "High water and humidity tolerance with balanced nitrogen ensures high paddy yield.",
  "alternatives": [
    {
      "crop": "Jute",
      "confidence": 3.2,
      "description": "Warm, humid tropical climate with abundant monsoon rainfall is optimal for fibrous vegetative growth."
    }
  ],
  "timestamp": "2026-11-01T15:00:00Z",
  "record_id": 12,
  "persisted": true,
  "persistence_error": null
}
```

### `POST /api/crop-guidance` (Path B: No Soil Report)
Generates rule-based agro-climatic rotations and advisories.
- No probability score is produced. `persisted` and `persistence_error`
  report whether the guidance history record was saved.
- **Request Body:**
```json
{
  "location": "Jharkhand",
  "season": "Kharif",
  "water_availability": "Moderate",
  "irrigation_available": true,
  "soil_type": "Loamy",
  "previous_crop": "Wheat"
}
```
- **Response `200 OK`:**
```json
{
  "status": "guided_recommendation",
  "location": "Jharkhand",
  "region": "Eastern India",
  "season": "Kharif",
  "recommendations": [
    {
      "crop": "Rice",
      "reason": "Rice is widely cultivated during the monsoon season...",
      "matching_factors": [
        "Rice is listed for the Eastern India context.",
        "It is suitable for the Kharif season."
      ]
    }
  ],
  "soil_test_required": true,
  "message": "These are preliminary crop suggestions based on the information provided...",
  "timestamp": "2026-11-01T15:00:00Z",
  "record_id": 13,
  "persisted": true,
  "persistence_error": null
}
```

---

## 4. Plant Disease Detection Endpoints

### `POST /api/disease/predict`
Uploads a foliar image for validation, preprocessing, and neural diagnosis.
- **Content-Type:** `multipart/form-data`
- **Form Field:** `file` (Binary image file: JPG, PNG, WEBP)
- The decoded Pillow image format must actually be JPEG, PNG, or WEBP; the
  filename extension alone is not accepted as proof of format. The legacy
  `confidence` response field is a model output score, not an empirically
  calibrated probability.
- Obvious portraits and scanned documents are rejected. Images without enough
  foliage cues or with an ambiguous model result return `200 OK` with
  `model_status` set to `uncertain_image` or `uncertain_prediction`,
  `prediction: null`, and `persisted: false`; no disease record is created.
  These lightweight visual checks are not a dedicated plant-vs-non-plant
  classifier and cannot identify every unrelated image.
- **Response `200 OK`:**
```json
{
  "model_status": "inferred_successfully",
  "model_loaded": true,
  "filename": "tomato_leaf.jpg",
  "image_details": {
    "dimensions": "224x224",
    "status": "Inference completed via MobileNetV2 architecture"
  },
  "message": "Diagnosis completed with a model score.",
  "prediction": "Early Blight",
  "confidence": 92.4,
  "supported_classes": [...],
  "persisted": true,
  "persistence_error": null
}
```
- Clear invalid images return `400 Bad Request` with a request to upload a clear
  crop leaf photograph.

### `GET /api/disease/classes`
Returns all 27 supported plant disease classes across 6 species.

### `GET /api/disease/classes/{class_id}`
Returns symptoms and 3-tier treatments (organic, chemical, cultural) for a specific disease.

---

## 5. History & Analytics Endpoints

### `GET /api/history`
Returns the authenticated user's unified history of crop recommendations and disease inspections.
Authenticated users receive their own records; unauthenticated requests receive
guest/community records. The `date` field is formatted in Asia/Kolkata, while
`timestamp` remains an unambiguous UTC ISO-8601 value.

### `DELETE /api/history/{id}`
Deletes a prediction record owned by the authenticated user. Requires a valid
bearer token; records belonging to another user or to an unauthenticated guest
are reported as not found.

### `GET /api/analytics/summary`
Calculates aggregated soil averages ($N, P, K, pH$, rainfall), crop frequencies,
and farm health index for the authenticated user only. Requires a valid bearer token.
