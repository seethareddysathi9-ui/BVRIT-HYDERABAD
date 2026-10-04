from health_analysis import analyze_child
from screening_summary import create_screening_summary


def run_person4_screening(
    age,
    sex,
    height,
    weight,
    image_path
):
    """
    Main interface for Person 4.

    Other team members can call this function
    without needing to know the internal implementation.
    """

    result = analyze_child(
        age=age,
        sex=sex,
        height=height,
        weight=weight,
        image_path=image_path
    )

    summary = create_screening_summary(result)

    return summary


if __name__ == "__main__":

    result = run_person4_screening(
        age=5,
        sex="female",
        height=104,
        weight=14,
        image_path="child.jpeg"
    )

    print("\n========== PERSON 4 MODULE TEST ==========\n")
    print(result)
    print("\n==========================================\n")