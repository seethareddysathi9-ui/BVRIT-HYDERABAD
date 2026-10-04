from PIL import Image, ImageStat, ImageFilter, ImageChops
from growth_assessment import assess_growth


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def analyze_image(image_path):
    """
    Performs non-diagnostic computer-vision analysis.

    The current implementation uses Pillow to extract
    objective image-quality and visual properties.

    It does NOT diagnose anemia, malnutrition, or any
    other medical condition.
    """

    image = Image.open(image_path).convert("RGB")

    width, height = image.size

    # --------------------------------------------------------
    # 1. Convert image to grayscale
    # --------------------------------------------------------

    grayscale = image.convert("L")

    # --------------------------------------------------------
    # 2. Brightness
    # --------------------------------------------------------

    brightness = ImageStat.Stat(
        grayscale
    ).mean[0]

    # --------------------------------------------------------
    # 3. Contrast
    # --------------------------------------------------------

    contrast = ImageStat.Stat(
        grayscale
    ).stddev[0]

    # --------------------------------------------------------
    # 4. Edge-based clarity
    # --------------------------------------------------------

    edge_image = grayscale.filter(
        ImageFilter.FIND_EDGES
    )

    edge_strength = ImageStat.Stat(
        edge_image
    ).mean[0]

    # --------------------------------------------------------
    # 5. Brightness uniformity
    # --------------------------------------------------------
    #
    # Divide the image into four regions and compare
    # their average brightness.
    #
    # This helps identify strongly uneven lighting.
    # It is NOT a medical measurement.
    # --------------------------------------------------------

    half_width = width // 2
    half_height = height // 2

    regions = [
        image.crop((0, 0, half_width, half_height)),
        image.crop((half_width, 0, width, half_height)),
        image.crop((0, half_height, half_width, height)),
        image.crop(
            (half_width, half_height, width, height)
        )
    ]

    region_brightness = []

    for region in regions:
        region_gray = region.convert("L")

        region_mean = ImageStat.Stat(
            region_gray
        ).mean[0]

        region_brightness.append(
            round(region_mean, 2)
        )

    brightness_range = (
        max(region_brightness)
        - min(region_brightness)
    )

    if brightness_range <= 35:
        lighting_uniformity = "good"

    elif brightness_range <= 70:
        lighting_uniformity = "acceptable"

    else:
        lighting_uniformity = "uneven"

    # --------------------------------------------------------
    # 6. Basic color information
    # --------------------------------------------------------

    rgb_stat = ImageStat.Stat(image)

    red_mean = rgb_stat.mean[0]
    green_mean = rgb_stat.mean[1]
    blue_mean = rgb_stat.mean[2]

    colorfulness = (
        max(red_mean, green_mean, blue_mean)
        - min(red_mean, green_mean, blue_mean)
    )

    if colorfulness < 15:
        color_information = "low"

    elif colorfulness < 45:
        color_information = "moderate"

    else:
        color_information = "good"

    # --------------------------------------------------------
    # 7. Quality issues
    # --------------------------------------------------------

    quality_issues = []

    if width < 300 or height < 300:
        quality_issues.append(
            "low_resolution"
        )

    if brightness < 40:
        quality_issues.append(
            "too_dark"
        )

    elif brightness > 235:
        quality_issues.append(
            "too_bright"
        )

    if contrast < 15:
        quality_issues.append(
            "low_contrast"
        )

    if edge_strength < 3:
        quality_issues.append(
            "low_clarity"
        )

    if lighting_uniformity == "uneven":
        quality_issues.append(
            "uneven_lighting"
        )

    # --------------------------------------------------------
    # 8. Overall image quality
    # --------------------------------------------------------

    if len(quality_issues) == 0:

        image_quality = "good"

    elif len(quality_issues) <= 2:

        image_quality = "acceptable"

    else:

        image_quality = "poor"

    # --------------------------------------------------------
    # 9. Return computer-vision information
    # --------------------------------------------------------

    return {

        "image_quality": image_quality,

        "image_width": width,
        "image_height": height,

        "average_brightness": round(
            brightness,
            2
        ),

        "contrast_score": round(
            contrast,
            2
        ),

        "clarity_score": round(
            edge_strength,
            2
        ),

        "brightness_range": round(
            brightness_range,
            2
        ),

        "lighting_uniformity":
            lighting_uniformity,

        "red_mean": round(
            red_mean,
            2
        ),

        "green_mean": round(
            green_mean,
            2
        ),

        "blue_mean": round(
            blue_mean,
            2
        ),

        "colorfulness_score": round(
            colorfulness,
            2
        ),

        "color_information":
            color_information,

        "region_brightness":
            region_brightness,

        "quality_issues":
            quality_issues,

        # ----------------------------------------------------
        # Medical visual indicators
        # ----------------------------------------------------
        #
        # These remain unavailable until a validated
        # medical computer-vision model is connected.
        #

        "possible_pallor_indicator":
            "not_assessed",

        "visible_rib_prominence":
            "not_assessed",

        "general_appearance":
            "not_assessed",

        "medical_visual_model":
            "not_connected"
    }


# ============================================================
# GROWTH SCREENING INTERPRETATION
# ============================================================

def interpret_growth_screening(growth_result):
    """
    Converts WHO reference-band information into a
    simple screening interpretation.

    This is NOT a medical diagnosis.
    """

    if not isinstance(
        growth_result,
        dict
    ):
        return {
            "status": "unavailable",
            "message":
                "Growth assessment unavailable."
        }

    if growth_result.get(
        "status"
    ) != "success":

        return {
            "status": "unavailable",
            "message":
                growth_result.get(
                    "assessment",
                    "Growth reference unavailable."
                )
        }

    height_position = growth_result.get(
        "height_position",
        "unknown"
    )

    weight_position = growth_result.get(
        "weight_position",
        "unknown"
    )

    below_height_reference = (
        height_position
        in [
            "below_-3_SD",
            "between_-3_and_-2_SD"
        ]
    )

    below_weight_reference = (
        weight_position
        in [
            "below_-3_SD",
            "between_-3_and_-2_SD"
        ]
    )

    if (
        below_height_reference
        or below_weight_reference
    ):

        screening_priority = (
            "further_assessment"
        )

        message = (
            "One or more measurements fall "
            "below the -2 SD reference band. "
            "Further assessment is recommended."
        )

    else:

        screening_priority = (
            "routine_review"
        )

        message = (
            "Measurements are within the "
            "available WHO reference bands "
            "used by this screening module."
        )

    return {

        "status": "available",

        "height_reference_band":
            height_position,

        "weight_reference_band":
            weight_position,

        "screening_priority":
            screening_priority,

        "message":
            message
    }


# ============================================================
# OVERALL SCREENING PRIORITY
# ============================================================

def calculate_overall_risk(
    visual_screening,
    growth_result
):
    """
    Combines image-quality information and growth
    screening information.

    This function does NOT diagnose a medical condition.

    The returned value represents screening priority,
    not disease status.
    """

    growth_interpretation = (
        interpret_growth_screening(
            growth_result
        )
    )

    if (
        growth_interpretation.get(
            "status"
        ) != "available"
    ):

        return "PENDING"

    # --------------------------------------------------------
    # Poor image quality
    # --------------------------------------------------------

    if visual_screening.get(
        "image_quality"
    ) == "poor":

        return "IMAGE_REVIEW_REQUIRED"

    # --------------------------------------------------------
    # Growth reference indicates need for
    # further assessment.
    # --------------------------------------------------------

    if growth_interpretation.get(
        "screening_priority"
    ) == "further_assessment":

        return "FURTHER_ASSESSMENT"

    # --------------------------------------------------------
    # No validated medical vision model
    # is currently connected.
    # --------------------------------------------------------

    return "ROUTINE_SCREENING"


# ============================================================
# COMPLETE CHILD ANALYSIS
# ============================================================

def analyze_child(
    age,
    sex,
    height,
    weight,
    image_path
):
    """
    Main Poshan AI screening function.

    Pipeline:

    1. Validate and load image
    2. Analyze image quality
    3. Extract objective visual properties
    4. Perform WHO growth-reference screening
    5. Interpret reference bands
    6. Generate screening priority

    This is an AI-assisted screening system,
    not a medical diagnosis.
    """

    try:

        # ----------------------------------------------------
        # STEP 1: Load image
        # ----------------------------------------------------

        image = Image.open(
            image_path
        ).convert("RGB")

        # ----------------------------------------------------
        # STEP 2: Computer-vision analysis
        # ----------------------------------------------------

        visual_result = analyze_image(
            image_path
        )

        # ----------------------------------------------------
        # STEP 3: Growth assessment
        # ----------------------------------------------------

        growth_result = assess_growth(
            age_years=age,
            sex=sex,
            height_cm=height,
            weight_kg=weight
        )

        # ----------------------------------------------------
        # STEP 4: Interpret growth result
        # ----------------------------------------------------

        growth_interpretation = (
            interpret_growth_screening(
                growth_result
            )
        )

        # ----------------------------------------------------
        # STEP 5: Calculate screening priority
        # ----------------------------------------------------

        overall_risk = (
            calculate_overall_risk(
                visual_result,
                growth_result
            )
        )

        # ----------------------------------------------------
        # STEP 6: Prepare complete result
        # ----------------------------------------------------

        result = {

            "status": "success",

            "child_information": {

                "age_years": age,

                "sex": sex,

                "height_cm": height,

                "weight_kg": weight
            },

            "image_information": {

                "width":
                    image.size[0],

                "height":
                    image.size[1]
            },

            "visual_screening":
                visual_result,

            "growth_assessment":
                growth_result,

            "growth_interpretation":
                growth_interpretation,

            "overall_risk":
                overall_risk,

            "system_capabilities": {

                "image_quality_analysis":
                    True,

                "who_growth_reference":
                    True,

                "medical_visual_ai":
                    False
            },

            "disclaimer": (

                "This is an AI-assisted "
                "screening result, not a "
                "medical diagnosis. Clinical "
                "evaluation is recommended "
                "when indicated."
            )
        }

        return result

    except Exception as error:

        return {

            "status": "error",

            "message": str(error),

            "overall_risk": "PENDING",

            "disclaimer": (

                "This is an AI-assisted "
                "screening result, not a "
                "medical diagnosis."
            )
        }


# ============================================================
# TEST THE COMPLETE PIPELINE
# ============================================================

if __name__ == "__main__":

    result = analyze_child(

        age=5,

        sex="female",

        height=102,

        weight=14,

        image_path="child.jpeg"
    )

    print(
        "\n========== POSHAN AI SCREENING RESULT ==========\n"
    )

    print("Status:")
    print(
        result["status"]
    )

    print("\nChild Information:")
    print(
        result["child_information"]
    )

    print("\nImage Information:")
    print(
        result["image_information"]
    )

    print("\nVisual Screening:")
    print(
        result["visual_screening"]
    )

    print("\nGrowth Assessment:")
    print(
        result["growth_assessment"]
    )

    print("\nGrowth Interpretation:")
    print(
        result["growth_interpretation"]
    )

    print("\nOverall Screening Priority:")
    print(
        result["overall_risk"]
    )

    print("\nSystem Capabilities:")
    print(
        result["system_capabilities"]
    )

    print("\nDisclaimer:")
    print(
        result["disclaimer"]
    )

    print(
        "\n=================================================\n"
    )