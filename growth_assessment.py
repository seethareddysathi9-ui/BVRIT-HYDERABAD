from growth_reference import get_growth_reference


def assess_growth(age_years, sex, height_cm, weight_kg):
    """
    Performs growth screening using validated WHO reference data.

    This is a screening tool and does NOT diagnose malnutrition
    or any other medical condition.
    """

    # -----------------------------
    # STEP 1: Validate age
    # -----------------------------
    if age_years < 0:
        return {
            "status": "invalid",
            "message": "Age cannot be negative."
        }

    # -----------------------------
    # STEP 2: Validate height
    # -----------------------------
    if height_cm <= 0:
        return {
            "status": "invalid",
            "message": "Height must be greater than zero."
        }

    # -----------------------------
    # STEP 3: Validate weight
    # -----------------------------
    if weight_kg <= 0:
        return {
            "status": "invalid",
            "message": "Weight must be greater than zero."
        }

    # -----------------------------
    # STEP 4: Validate sex
    # -----------------------------
    sex = sex.lower()

    if sex not in ["male", "female"]:
        return {
            "status": "invalid",
            "message": "Sex must be male or female."
        }

    # -----------------------------
    # STEP 5: Convert age to months
    # -----------------------------
    age_months = round(age_years * 12)

    # -----------------------------
    # STEP 6: Check WHO age range
    # -----------------------------
    if age_months > 60:
        return {
            "status": "reference_required",
            "age_months": age_months,
            "reference": "WHO 5-19 years",
            "assessment": (
                "This age requires the WHO 5-19 years reference."
            )
        }

    # -----------------------------
    # STEP 7: Get WHO reference
    # -----------------------------
    reference_result = get_growth_reference(
        age_months=age_months,
        sex=sex,
        height_cm=height_cm,
        weight_kg=weight_kg
    )

    # -----------------------------
    # STEP 8: Handle reference error
    # -----------------------------
    if reference_result.get("status") != "success":
        return reference_result

    # -----------------------------
    # STEP 9: Return growth result
    # -----------------------------
    return {
        "status": "success",

        "age_months": age_months,

        "sex": sex,

        "height_cm": height_cm,

        "height_position": reference_result.get(
            "height_position"
        ),

        "weight_kg": weight_kg,

        "weight_position": reference_result.get(
            "weight_position"
        ),

        "height_reference": reference_result.get(
            "height_reference"
        ),

        "weight_reference": reference_result.get(
            "weight_reference"
        ),

        "reference": "WHO Child Growth Standards",

        "files_used": reference_result.get(
            "files_used"
        ),

        "disclaimer": (
            "This is an AI-assisted growth screening result, "
            "not a medical diagnosis. Clinical evaluation "
            "is recommended when indicated."
        )
    }


# ==========================================
# TEST THE MODULE
# ==========================================

if __name__ == "__main__":

    result = assess_growth(
        age_years=5,
        sex="female",
        height_cm=102,
        weight_kg=14
    )

    print("\n========== POSHAN AI GROWTH ASSESSMENT ==========\n")

    print("Status:")
    print(result.get("status"))

    print("\nAge:")
    print(result.get("age_months"), "months")

    print("\nSex:")
    print(result.get("sex"))

    print("\nHeight:")
    print(result.get("height_cm"), "cm")

    print("\nHeight Position:")
    print(result.get("height_position"))

    print("\nWeight:")
    print(result.get("weight_kg"), "kg")

    print("\nWeight Position:")
    print(result.get("weight_position"))

    print("\nHeight Reference:")
    print(result.get("height_reference"))

    print("\nWeight Reference:")
    print(result.get("weight_reference"))

    print("\nReference:")
    print(result.get("reference"))

    print("\nFiles Used:")
    print(result.get("files_used"))

    print("\nDisclaimer:")
    print(result.get("disclaimer"))

    print("\n==================================================\n")