def create_screening_summary(result):
    """
    Converts the technical Poshan AI screening result
    into a frontend-friendly summary.

    This is a screening tool and NOT a medical diagnosis.
    """

    if result.get("status") != "success":
        return {
            "status": "error",
            "message": result.get(
                "message",
                "Unable to generate screening summary."
            )
        }

    # ========================================================
    # CHILD INFORMATION
    # ========================================================

    child = result.get(
        "child_information",
        {}
    )

    # ========================================================
    # VISUAL / COMPUTER VISION INFORMATION
    # ========================================================

    visual = result.get(
        "visual_screening",
        {}
    )

    # ========================================================
    # GROWTH INFORMATION
    # ========================================================

    growth = result.get(
        "growth_assessment",
        {}
    )

    growth_interpretation = result.get(
        "growth_interpretation",
        {}
    )

    # ========================================================
    # REFERENCE-BAND NAMES
    # ========================================================

    position_names = {

        "below_-3_SD":
            "Below -3 SD",

        "between_-3_and_-2_SD":
            "Between -3 SD and -2 SD",

        "between_-2_and_-1_SD":
            "Between -2 SD and -1 SD",

        "within_-1_to_+1_SD":
            "Within -1 SD to +1 SD",

        "between_+1_and_+2_SD":
            "Between +1 SD and +2 SD",

        "between_+2_and_+3_SD":
            "Between +2 SD and +3 SD",

        "above_+3_SD":
            "Above +3 SD"
    }

    height_position = growth.get(
        "height_position",
        "unknown"
    )

    weight_position = growth.get(
        "weight_position",
        "unknown"
    )

    readable_height = position_names.get(
        height_position,
        "Reference band unavailable"
    )

    readable_weight = position_names.get(
        weight_position,
        "Reference band unavailable"
    )

    # ========================================================
    # IMAGE QUALITY
    # ========================================================

    image_quality = visual.get(
        "image_quality",
        "unknown"
    )

    brightness = visual.get(
        "average_brightness"
    )

    contrast = visual.get(
        "contrast_score"
    )

    clarity = visual.get(
        "clarity_score"
    )

    brightness_range = visual.get(
        "brightness_range"
    )

    lighting_uniformity = visual.get(
        "lighting_uniformity",
        "unknown"
    )

    color_information = visual.get(
        "color_information",
        "unknown"
    )

    colorfulness_score = visual.get(
        "colorfulness_score"
    )

    quality_issues = visual.get(
        "quality_issues",
        []
    )

    # ========================================================
    # VISUAL FEATURES
    # ========================================================

    red_mean = visual.get(
        "red_mean"
    )

    green_mean = visual.get(
        "green_mean"
    )

    blue_mean = visual.get(
        "blue_mean"
    )

    region_brightness = visual.get(
        "region_brightness",
        []
    )

    # ========================================================
    # MEDICAL VISION STATUS
    # ========================================================

    medical_visual_model = visual.get(
        "medical_visual_model",
        "not_connected"
    )

    pallor_indicator = visual.get(
        "possible_pallor_indicator",
        "not_assessed"
    )

    rib_indicator = visual.get(
        "visible_rib_prominence",
        "not_assessed"
    )

    general_appearance = visual.get(
        "general_appearance",
        "not_assessed"
    )

    # ========================================================
    # OVERALL SCREENING
    # ========================================================

    overall_status = result.get(
        "overall_risk",
        "PENDING"
    )

    screening_priority = growth_interpretation.get(
        "screening_priority",
        "unavailable"
    )

    screening_message = growth_interpretation.get(
        "message",
        "Screening interpretation unavailable."
    )

    # ========================================================
    # SYSTEM CAPABILITIES
    # ========================================================

    capabilities = result.get(
        "system_capabilities",
        {}
    )

    # ========================================================
    # RETURN FRONTEND-FRIENDLY RESULT
    # ========================================================

    return {

        "status": "success",

        # ----------------------------------------------------
        # Child
        # ----------------------------------------------------

        "child": {

            "age": child.get(
                "age_years"
            ),

            "sex": child.get(
                "sex"
            ),

            "height_cm": child.get(
                "height_cm"
            ),

            "weight_kg": child.get(
                "weight_kg"
            )
        },

        # ----------------------------------------------------
        # Growth Screening
        # ----------------------------------------------------

        "growth_screening": {

            "age_months":
                growth.get(
                    "age_months"
                ),

            "height_reference_band":
                readable_height,

            "weight_reference_band":
                readable_weight,

            "height_position":
                height_position,

            "weight_position":
                weight_position,

            "screening_priority":
                screening_priority,

            "message":
                screening_message,

            "reference":
                growth.get(
                    "reference",
                    "WHO Child Growth Standards"
                )
        },

        # ----------------------------------------------------
        # Image Screening
        # ----------------------------------------------------

        "image_screening": {

            "image_quality":
                image_quality,

            "image_width":
                visual.get(
                    "image_width"
                ),

            "image_height":
                visual.get(
                    "image_height"
                ),

            "brightness":
                brightness,

            "contrast":
                contrast,

            "clarity":
                clarity,

            "brightness_range":
                brightness_range,

            "lighting_uniformity":
                lighting_uniformity,

            "color_information":
                color_information,

            "colorfulness_score":
                colorfulness_score,

            "quality_issues":
                quality_issues
        },

        # ----------------------------------------------------
        # Computer Vision Features
        # ----------------------------------------------------

        "computer_vision_features": {

            "red_mean":
                red_mean,

            "green_mean":
                green_mean,

            "blue_mean":
                blue_mean,

            "region_brightness":
                region_brightness,

            "pallor_indicator":
                pallor_indicator,

            "rib_prominence":
                rib_indicator,

            "general_appearance":
                general_appearance,

            "medical_visual_model":
                medical_visual_model
        },

        # ----------------------------------------------------
        # Overall Status
        # ----------------------------------------------------

        "overall_status":
            overall_status,

        # ----------------------------------------------------
        # System Capabilities
        # ----------------------------------------------------

        "system_capabilities": {

            "image_quality_analysis":
                capabilities.get(
                    "image_quality_analysis",
                    False
                ),

            "who_growth_reference":
                capabilities.get(
                    "who_growth_reference",
                    False
                ),

            "medical_visual_ai":
                capabilities.get(
                    "medical_visual_ai",
                    False
                )
        },

        # ----------------------------------------------------
        # Reference
        # ----------------------------------------------------

        "reference":
            "WHO Child Growth Standards",

        # ----------------------------------------------------
        # Disclaimer
        # ----------------------------------------------------

        "disclaimer": (

            "This is an AI-assisted "
            "screening result, not a "
            "medical diagnosis. Clinical "
            "evaluation is recommended "
            "when indicated."
        )
    }


# ============================================================
# TEST SUMMARY
# ============================================================

if __name__ == "__main__":

    from health_analysis import analyze_child

    result = analyze_child(

        age=5,

        sex="female",

        height=102,

        weight=14,

        image_path="child.jpeg"
    )

    summary = create_screening_summary(
        result
    )

    print(
        "\n========== POSHAN AI SCREENING SUMMARY ==========\n"
    )

    print("Status:")
    print(
        summary["status"]
    )

    print("\nChild:")
    print(
        summary["child"]
    )

    print("\nGrowth Screening:")

    print(
        "Age:",
        summary["growth_screening"][
            "age_months"
        ],
        "months"
    )

    print(
        "Height:",
        summary["growth_screening"][
            "height_reference_band"
        ]
    )

    print(
        "Weight:",
        summary["growth_screening"][
            "weight_reference_band"
        ]
    )

    print(
        "Priority:",
        summary["growth_screening"][
            "screening_priority"
        ]
    )

    print(
        "Message:",
        summary["growth_screening"][
            "message"
        ]
    )

    print("\nImage Screening:")

    print(
        "Quality:",
        summary["image_screening"][
            "image_quality"
        ]
    )

    print(
        "Resolution:",
        summary["image_screening"][
            "image_width"
        ],
        "x",
        summary["image_screening"][
            "image_height"
        ]
    )

    print(
        "Brightness:",
        summary["image_screening"][
            "brightness"
        ]
    )

    print(
        "Contrast:",
        summary["image_screening"][
            "contrast"
        ]
    )

    print(
        "Clarity:",
        summary["image_screening"][
            "clarity"
        ]
    )

    print(
        "Lighting:",
        summary["image_screening"][
            "lighting_uniformity"
        ]
    )

    print(
        "Color Information:",
        summary["image_screening"][
            "color_information"
        ]
    )

    print(
        "Quality Issues:",
        summary["image_screening"][
            "quality_issues"
        ]
    )

    print("\nComputer Vision Features:")

    print(
        summary[
            "computer_vision_features"
        ]
    )

    print("\nOverall Status:")
    print(
        summary["overall_status"]
    )

    print("\nSystem Capabilities:")
    print(
        summary["system_capabilities"]
    )

    print("\nReference:")
    print(
        summary["reference"]
    )

    print("\nDisclaimer:")
    print(
        summary["disclaimer"]
    )

    print(
        "\n=================================================\n"
    )