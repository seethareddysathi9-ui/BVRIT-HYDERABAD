import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

WHO_FOLDER = Path("WHO_Data")


def read_first_rows(excel_file, number_of_rows=8):

    with zipfile.ZipFile(excel_file, "r") as workbook:

        # Read shared strings
        shared_strings = []

        if "xl/sharedStrings.xml" in workbook.namelist():

            xml_data = workbook.read("xl/sharedStrings.xml")
            root = ET.fromstring(xml_data)

            namespace = {
                "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
            }

            for item in root.findall("main:si", namespace):
                text_parts = []

                for text in item.iter(
                    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
                ):
                    text_parts.append(text.text or "")

                shared_strings.append("".join(text_parts))

        # Read first worksheet
        sheet_files = [
            name for name in workbook.namelist()
            if name.startswith("xl/worksheets/sheet")
        ]

        if not sheet_files:
            print("No worksheet found.")
            return

        sheet_xml = workbook.read(sheet_files[0])
        root = ET.fromstring(sheet_xml)

        namespace = {
            "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        }

        rows = root.findall(".//main:sheetData/main:row", namespace)

        print(f"\nFile: {excel_file.name}")
        print("-" * 70)

        for row in rows[:number_of_rows]:

            values = []

            for cell in row.findall("main:c", namespace):

                cell_type = cell.attrib.get("t")
                value = cell.find("main:v", namespace)

                if value is None:
                    values.append("")
                    continue

                text = value.text

                if cell_type == "s":
                    text = shared_strings[int(text)]

                values.append(text)

            print(values)


print("\n========== WHO DATA PREVIEW ==========")

files = list(WHO_FOLDER.glob("*.xlsx"))

for file in files:
    read_first_rows(file)

print("\n======================================")