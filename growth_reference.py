import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


# ============================================================
# POSHAN AI - WHO GROWTH REFERENCE
# ============================================================

PROJECT_FOLDER = Path(__file__).resolve().parent
WHO_FOLDER = PROJECT_FOLDER / "WHO_Data"


# ============================================================
# READ XLSX FILE
# ============================================================

def read_excel_rows(file_path):

    with zipfile.ZipFile(file_path, "r") as workbook:

        # Read shared strings
        shared_strings = []

        if "xl/sharedStrings.xml" in workbook.namelist():

            root = ET.fromstring(
                workbook.read("xl/sharedStrings.xml")
            )

            namespace = {
                "main":
                "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
            }

            for item in root.findall("main:si", namespace):

                text_parts = []

                for text in item.iter(
                    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
                ):
                    text_parts.append(text.text or "")

                shared_strings.append(
                    "".join(text_parts)
                )

        # Find worksheet
        sheet_files = [
            name
            for name in workbook.namelist()
            if name.startswith("xl/worksheets/sheet")
        ]

        if not sheet_files:
            raise ValueError(
                f"No worksheet found in {file_path.name}"
            )

        root = ET.fromstring(
            workbook.read(sheet_files[0])
        )

        namespace = {
            "main":
            "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        }

        rows = root.findall(
            ".//main:sheetData/main:row",
            namespace
        )

        if not rows:
            return []

        headers = []
        result = []

        for row_number, row in enumerate(rows):

            values = []

            for cell in row.findall(
                "main:c",
                namespace
            ):

                cell_type = cell.attrib.get("t")

                value = cell.find(
                    "main:v",
                    namespace
                )

                if value is None:
                    values.append("")
                    continue

                text = value.text or ""

                if cell_type == "s":

                    try:
                        text = shared_strings[int(text)]
                    except (IndexError, ValueError):
                        text = ""

                values.append(text)

            # First row = headers
            if row_number == 0:

                headers = [
                    value.strip()
                    for value in values
                ]

            else:

                row_data = {}

                for index, value in enumerate(values):

                    if index < len(headers):

                        row_data[
                            headers[index]
                        ] = value

                result.append(row_data)

        return result


# ============================================================
# FIND WHO FILE
# ============================================================

def find_who_file(prefix):

    if not WHO_FOLDER.exists():
        return None

    for file in WHO_FOLDER.glob("*.xlsx"):

        if file.name.lower().startswith(
            prefix.lower()
        ):
            return file

    return None


# ============================================================
# WHO GROWTH REFERENCE
# ============================================================

def get_growth_reference(
    age_months,
    sex,
    height_cm,
    weight_kg
):

    sex = str(sex).lower().strip()

    # Validate sex
    if sex not in ["male", "female"]:

        return {
            "status": "invalid",
            "message":
            "Sex must be male or female."
        }

    # Validate age
    if age_months < 0:

        return {
            "status": "invalid",
            "message":
            "Age cannot be negative."
        }

    # Validate height
    if height_cm <= 0:

        return {
            "status": "invalid",
            "message":
            "Height must be greater than zero."
        }

    # Validate weight
    if weight_kg <= 0:

        return {
            "status": "invalid",
            "message":
            "Weight must be greater than zero."
        }

    # ========================================================
    # IMPORTANT:
    # Python uses male/female.
    # WHO filenames use boys/girls.
    # ========================================================

    if sex == "female":
        who_sex_name = "girls"
    else:
        who_sex_name = "boys"

    # WHO filenames
    weight_prefix = (
        f"wfa_{who_sex_name}_0-to-5-years"
    )

    height_prefix = (
        f"lhfa_{who_sex_name}_2-to-5-years"
    )

    # Find files
    weight_file = find_who_file(
        weight_prefix
    )

    height_file = find_who_file(
        height_prefix
    )

    # Check weight file
    if weight_file is None:

        return {
            "status": "reference_missing",
            "message":
            f"WHO weight-for-age file not found for {sex}.",
            "expected":
            weight_prefix
        }

    # Check height file
    if height_file is None:

        return {
            "status": "reference_missing",
            "message":
            f"WHO height-for-age file not found for {sex}.",
            "expected":
            height_prefix
        }

    # ========================================================
    # Read Excel files
    # ========================================================

    try:

        weight_rows = read_excel_rows(
            weight_file
        )

        height_rows = read_excel_rows(
            height_file
        )

    except Exception as error:

        return {
            "status": "reference_error",
            "message": str(error)
        }

    # ========================================================
    # Find matching age
    # ========================================================

    weight_row = None
    height_row = None

    for row in weight_rows:

        month = str(
            row.get("Month", "")
        ).strip()

        if month == str(age_months):

            weight_row = row
            break

    for row in height_rows:

        month = str(
            row.get("Month", "")
        ).strip()

        if month == str(age_months):

            height_row = row
            break

    # Check weight age
    if weight_row is None:

        return {
            "status": "age_not_available",
            "message":
            "WHO weight reference is not available "
            "for this age.",
            "age_months":
            age_months
        }

    # Check height age
    if height_row is None:

        return {
            "status": "age_not_available",
            "message":
            "WHO height reference is not available "
            "for this age.",
            "age_months":
            age_months
        }

    # ========================================================
    # Convert numbers
    # ========================================================

    def get_number(row, column):

        try:

            return float(
                str(
                    row.get(column, "")
                ).strip()
            )

        except (ValueError, TypeError):

            return None

    # Weight reference
    weight_reference = {

        "SD3neg":
        get_number(weight_row, "SD3neg"),

        "SD2neg":
        get_number(weight_row, "SD2neg"),

        "SD1neg":
        get_number(weight_row, "SD1neg"),

        "SD0":
        get_number(weight_row, "SD0"),

        "SD1":
        get_number(weight_row, "SD1"),

        "SD2":
        get_number(weight_row, "SD2"),

        "SD3":
        get_number(weight_row, "SD3")
    }

    # Height reference
    height_reference = {

        "SD3neg":
        get_number(height_row, "SD3neg"),

        "SD2neg":
        get_number(height_row, "SD2neg"),

        "SD1neg":
        get_number(height_row, "SD1neg"),

        "SD0":
        get_number(height_row, "SD0"),

        "SD1":
        get_number(height_row, "SD1"),

        "SD2":
        get_number(height_row, "SD2"),

        "SD3":
        get_number(height_row, "SD3")
    }

    # ========================================================
    # Compare measurement with WHO reference bands
    # ========================================================

    def classify(value, reference):

        if value < reference["SD3neg"]:

            return "below_-3_SD"

        elif value < reference["SD2neg"]:

            return "between_-3_and_-2_SD"

        elif value < reference["SD1neg"]:

            return "between_-2_and_-1_SD"

        elif value <= reference["SD1"]:

            return "within_-1_to_+1_SD"

        elif value <= reference["SD2"]:

            return "between_+1_and_+2_SD"

        elif value <= reference["SD3"]:

            return "between_+2_and_+3_SD"

        else:

            return "above_+3_SD"

    # Calculate positions
    height_position = classify(
        height_cm,
        height_reference
    )

    weight_position = classify(
        weight_kg,
        weight_reference
    )

    # ========================================================
    # Final result
    # ========================================================

    return {

        "status":
        "success",

        "age_months":
        age_months,

        "sex":
        sex,

        "measured_height_cm":
        height_cm,

        "measured_weight_kg":
        weight_kg,

        "height_position":
        height_position,

        "weight_position":
        weight_position,

        "height_reference":
        height_reference,

        "weight_reference":
        weight_reference,

        "reference_source":
        "WHO Child Growth Standards",

        "files_used": {

            "height":
            height_file.name,

            "weight":
            weight_file.name
        },

        "disclaimer":
        "This is an AI-assisted growth screening "
        "result, not a medical diagnosis. Clinical "
        "evaluation is recommended when indicated."
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n========== POSHAN AI WHO TEST ==========\n"
    )

    print("WHO folder:")
    print(WHO_FOLDER)

    print("\nWHO folder exists:")
    print(WHO_FOLDER.exists())

    print("\nFiles found:")

    if WHO_FOLDER.exists():

        for file in WHO_FOLDER.glob("*.xlsx"):
            print(" -", file.name)

    # Demo child
    result = get_growth_reference(
        age_months=60,
        sex="female",
        height_cm=102,
        weight_kg=14
    )

    print(
        "\n========== RESULT ==========\n"
    )

    print(
        "Status:",
        result.get("status")
    )

    if result.get("status") != "success":

        print(
            "Message:",
            result.get(
                "message",
                "Unknown error"
            )
        )

        if "expected" in result:
            print(
                "Expected:",
                result["expected"]
            )

    else:

        print(
            "Age:",
            result["age_months"],
            "months"
        )

        print(
            "Sex:",
            result["sex"]
        )

        print(
            "Height:",
            result["measured_height_cm"],
            "cm"
        )

        print(
            "Height position:",
            result["height_position"]
        )

        print(
            "Weight:",
            result["measured_weight_kg"],
            "kg"
        )

        print(
            "Weight position:",
            result["weight_position"]
        )

        print(
            "\nHeight reference:"
        )

        print(
            result["height_reference"]
        )

        print(
            "\nWeight reference:"
        )

        print(
            result["weight_reference"]
        )

        print(
            "\nFiles used:"
        )

        print(
            result["files_used"]
        )

        print(
            "\nReference:"
        )

        print(
            result["reference_source"]
        )

        print(
            "\nDisclaimer:"
        )

        print(
            result["disclaimer"]
        )

    print(
        "\n============================\n"
    )