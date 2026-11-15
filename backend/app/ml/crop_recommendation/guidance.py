"""
KrishiVision - Preliminary Crop Guidance Engine

This engine is used when the farmer does not have a soil report.

It does NOT replace the Random Forest ML model.
"""

from .guidance_data import CROP_GUIDANCE, STATE_REGIONS


def normalize(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def get_region_from_location(location):
    """
    Resolve a provided state/location context to a broad region.

    The current MVP expects a state name.
    City-to-state resolution can be added later.
    """

    location_normalized = normalize(location)

    return STATE_REGIONS.get(location_normalized)


def get_crop_guidance(
    location,
    season,
    previous_crop=None,
    irrigation_available=None,
    water_availability=None,
    soil_type=None,
):
    """
    Generate preliminary crop guidance.

    This is a rule-based guidance system.
    It is NOT an ML prediction and does not produce
    an ML confidence score.
    """

    region = get_region_from_location(location)

    season_normalized = normalize(season)
    water_normalized = normalize(water_availability)
    irrigation_normalized = normalize(irrigation_available)
    soil_normalized = normalize(soil_type)
    previous_crop_normalized = normalize(previous_crop)

    recommendations = []

    for crop_key, crop in CROP_GUIDANCE.items():

        score = 0
        reasons = []

        # =========================================================
        # 1. REGION
        # =========================================================
        if region:
            crop_regions = [
                normalize(item)
                for item in crop["regions"]
            ]

            if normalize(region) in crop_regions:
                score += 3
                reasons.append(
                    f"{crop['display_name']} is listed for the "
                    f"{region} context."
                )
            else:
                # Don't recommend a crop if its known regional
                # context doesn't match.
                continue

        # =========================================================
        # 2. SEASON
        # =========================================================
        if season_normalized:
            crop_seasons = [
                normalize(item)
                for item in crop["seasons"]
            ]

            if season_normalized in crop_seasons:
                score += 4
                reasons.append(
                    f"It is suitable for the {season} season."
                )
            else:
                # Season mismatch is a hard filter.
                continue

        # =========================================================
        # 3. WATER AVAILABILITY
        # =========================================================
        crop_water = normalize(crop["water_requirement"])

        if water_normalized:

            if water_normalized == "low":

                if crop_water == "low":
                    score += 3
                    reasons.append(
                        "Its general water requirement is relatively low."
                    )

                elif crop_water == "moderate":
                    score += 1
                    reasons.append(
                        "It has a moderate water requirement, so "
                        "water availability should be monitored."
                    )

                else:
                    # High-water crops are not recommended when
                    # the farmer reports low water availability.
                    continue

            elif water_normalized == "moderate":

                if crop_water == "low":
                    score += 3
                    reasons.append(
                        "Its general water requirement is relatively low "
                        "and is compatible with moderate water availability."
                    )

                elif crop_water == "moderate":
                    score += 3
                    reasons.append(
                        "Its general water requirement matches "
                        "moderate water availability."
                    )

                elif crop_water == "high":
                    score += 1
                    reasons.append(
                        "It generally needs more water, so adequate "
                        "water management is important."
                    )

            elif water_normalized == "high":

                if crop_water == "high":
                    score += 3
                    reasons.append(
                        "Available water is compatible with its "
                        "higher water requirement."
                    )

                elif crop_water == "moderate":
                    score += 2
                    reasons.append(
                        "Available water is sufficient for its "
                        "general requirement."
                    )

                elif crop_water == "low":
                    score += 1
                    reasons.append(
                        "Water availability is sufficient, although "
                        "the crop generally requires less water."
                    )

        # =========================================================
        # 4. IRRIGATION
        # =========================================================
        if irrigation_normalized:

            irrigation_yes = irrigation_normalized in [
                "yes",
                "true",
                "available",
            ]

            irrigation_no = irrigation_normalized in [
                "no",
                "false",
                "not available",
            ]

            # Irrigation availability matters mainly when water
            # availability is limited or when the crop has higher
            # water needs.
            if irrigation_yes:

                if crop_water == "high":
                    score += 2
                    reasons.append(
                        "Irrigation is available, which can help "
                        "manage a higher water requirement."
                    )
                else:
                    score += 1
                    reasons.append(
                        "Irrigation is available."
                    )

            elif irrigation_no:

                if crop_water == "low":
                    score += 2
                    reasons.append(
                        "The crop has a relatively low water requirement "
                        "and irrigation is unavailable."
                    )

                elif crop_water == "moderate":
                    score += 1
                    reasons.append(
                        "Irrigation is unavailable, so moisture "
                        "management will be important."
                    )

                elif crop_water == "high":
                    # High-water crop without irrigation is not
                    # automatically rejected because rainfall/rainfed
                    # agriculture may still support it, but no bonus.
                    reasons.append(
                        "Irrigation is unavailable; adequate rainfall "
                        "and moisture conditions would be important."
                    )

        # =========================================================
        # 5. KNOWN SOIL TYPE
        # =========================================================
        if soil_normalized:

            crop_soils = [
                normalize(item)
                for item in crop["soil_types"]
            ]

            if soil_normalized in crop_soils:
                score += 2
                reasons.append(
                    f"The provided soil type ({soil_type}) "
                    f"is listed as suitable."
                )

        # =========================================================
        # 6. PREVIOUS CROP
        # =========================================================
        if previous_crop_normalized:

            # Avoid recommending the exact same crop as the
            # farmer's previous crop as a rotation preference.
            if previous_crop_normalized == crop_key:
                score -= 2
                reasons.append(
                    "It is the same as the previous crop, so "
                    "crop rotation considerations should be evaluated."
                )
            else:
                # We don't award a generic bonus simply because
                # the crop is different. The previous crop is
                # treated as contextual information.
                reasons.append(
                    f"Previous crop recorded as {previous_crop}."
                )

        # =========================================================
        # 7. MINIMUM SCORE
        # =========================================================
        if score >= 7:
            recommendations.append({
                "crop": crop["display_name"],
                "reason": crop["reason"],
                "matching_factors": reasons,
                "_score": score,
            })

    # Rank internally using the private suitability score
    recommendations.sort(
        key=lambda item: item["_score"],
        reverse=True
    )

    # Keep only the top 5 candidates
    recommendations = recommendations[:5]

    # Remove the internal score before returning data
    for recommendation in recommendations:
        recommendation.pop("_score", None)

    return {
        "location": location,
        "region": region,
        "season": season,
        "recommendations": recommendations,
        "soil_test_required": True,
        "message": (
            "These are preliminary crop suggestions based on the "
            "information provided. For a full soil-based ML "
            "recommendation, obtain N, P, K and pH values from "
            "a soil test report."
        ),
    }