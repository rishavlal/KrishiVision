"""
KrishiVision - Preliminary Crop Guidance Knowledge Base

This knowledge base is used ONLY when the farmer does not have
a soil test report.

It is NOT the Random Forest model.

The guidance engine uses:
- season
- water availability
- irrigation availability
- known soil type (optional)
- previous crop (contextual)
- location/state context
"""

CROP_GUIDANCE = {

    "rice": {
        "display_name": "Rice",
        "seasons": ["Kharif"],
        "water_requirement": "high",
        "irrigation_suitable": ["Yes", "No"],
        "soil_types": [
            "Loamy",
            "Clay",
            "Clay Loam"
        ],
        "regions": [
            "Eastern India",
            "Northern India",
            "Central India",
            "Southern India",
            "Northeastern India"
        ],
        "reason": (
            "Rice is widely cultivated during the monsoon season "
            "and can be grown under rainfed or irrigated conditions "
            "depending on the region and field conditions."
        ),
    },

    "maize": {
        "display_name": "Maize",
        "seasons": ["Kharif", "Rabi", "Zaid"],
        "water_requirement": "moderate",
        "irrigation_suitable": ["Yes", "No"],
        "soil_types": [
            "Loamy",
            "Sandy Loam",
            "Clay Loam"
        ],
        "regions": [
            "Eastern India",
            "Northern India",
            "Central India",
            "Southern India",
            "Northeastern India"
        ],
        "reason": (
            "Maize can be cultivated in multiple seasons in India, "
            "with suitability depending on regional climate, "
            "moisture availability and management."
        ),
    },

    "chickpea": {
        "display_name": "Chickpea",
        "seasons": ["Rabi"],
        "water_requirement": "low",
        "irrigation_suitable": ["Yes", "No"],
        "soil_types": [
            "Loamy",
            "Sandy Loam",
            "Clay Loam"
        ],
        "regions": [
            "Central India",
            "Northern India",
            "Eastern India"
        ],
        "reason": (
            "Chickpea is an important rabi pulse and can be grown "
            "under rainfed conditions in suitable regions."
        ),
    },

    "pigeonpea": {
        "display_name": "Pigeonpea",
        "seasons": ["Kharif"],
        "water_requirement": "low",
        "irrigation_suitable": ["Yes", "No"],
        "soil_types": [
            "Loamy",
            "Sandy Loam"
        ],
        "regions": [
            "Central India",
            "Eastern India",
            "Southern India"
        ],
        "reason": (
            "Pigeonpea is commonly grown as a rainfed kharif pulse "
            "and is suitable for regions where moisture can vary."
        ),
    },

    "wheat": {
        "display_name": "Wheat",
        "seasons": ["Rabi"],
        "water_requirement": "moderate",
        "irrigation_suitable": ["Yes", "No"],
        "soil_types": [
            "Loamy",
            "Clay Loam",
            "Sandy Loam"
        ],
        "regions": [
            "Northern India",
            "Central India",
            "Eastern India"
        ],
        "reason": (
            "Wheat is primarily a rabi crop and is widely cultivated "
            "in suitable winter-growing regions."
        ),
    },

    "mustard": {
        "display_name": "Mustard",
        "seasons": ["Rabi"],
        "water_requirement": "low",
        "irrigation_suitable": ["Yes", "No"],
        "soil_types": [
            "Loamy",
            "Sandy Loam",
            "Clay Loam"
        ],
        "regions": [
            "Northern India",
            "Central India",
            "Eastern India"
        ],
        "reason": (
            "Mustard is an important rabi oilseed and can be included "
            "in suitable crop rotations, including some rice-fallow systems."
        ),
    },

    "millets": {
        "display_name": "Millets",
        "seasons": ["Kharif"],
        "water_requirement": "low",
        "irrigation_suitable": ["Yes", "No"],
        "soil_types": [
            "Sandy Loam",
            "Loamy"
        ],
        "regions": [
            "Central India",
            "Northern India",
            "Southern India",
            "Eastern India"
        ],
        "reason": (
            "Millets generally require less water than many conventional "
            "cereal crops and are useful options in suitable rainfed areas."
        ),
    },
}


# Broad state-to-region context.
#
# This is intentionally separated from the crop data so that
# additional states/regions can be added without changing
# the recommendation engine.
STATE_REGIONS = {

    "jharkhand": "Eastern India",
    "bihar": "Eastern India",
    "west bengal": "Eastern India",
    "odisha": "Eastern India",
    "assam": "Northeastern India",

    "punjab": "Northern India",
    "haryana": "Northern India",
    "uttar pradesh": "Northern India",
    "uttarakhand": "Northern India",

    "madhya pradesh": "Central India",
    "chhattisgarh": "Central India",

    "rajasthan": "Northern India",

    "maharashtra": "Central India",
    "gujarat": "Central India",

    "karnataka": "Southern India",
    "telangana": "Southern India",
    "andhra pradesh": "Southern India",
    "tamil nadu": "Southern India",
    "kerala": "Southern India",

    "goa": "Southern India",
}