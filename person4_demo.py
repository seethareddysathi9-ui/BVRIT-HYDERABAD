from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import tempfile
import html

from health_analysis import analyze_child
from screening_summary import create_screening_summary


HOST = "127.0.0.1"
PORT = 8000


# =========================================================
# PAGE STYLE
# =========================================================

HTML_STYLE = """
<style>

    body {
        font-family: Arial, sans-serif;
        background: #f4f7fb;
        margin: 0;
        padding: 30px;
        color: #222;
    }

    .container {
        max-width: 950px;
        margin: auto;
    }

    .header {
        background: #173f5f;
        color: white;
        padding: 30px;
        border-radius: 14px;
        margin-bottom: 22px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    .header h1 {
        margin: 0 0 8px 0;
        font-size: 32px;
    }

    .header p {
        margin: 0;
        font-size: 17px;
    }

    .card {
        background: white;
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .card h2 {
        color: #173f5f;
        margin-top: 0;
    }

    .grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
    }

    .item {
        background: #f7f9fc;
        padding: 14px;
        border-radius: 8px;
    }

    .label {
        font-size: 13px;
        color: #666;
        margin-bottom: 5px;
    }

    .value {
        font-size: 18px;
        font-weight: bold;
    }

    .status {
        background: #fff8df;
        border-left: 6px solid #f0ad4e;
        padding: 20px;
        border-radius: 10px;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
    }

    .good {
        color: #198754;
    }

    .warning {
        color: #b7791f;
    }

    .neutral {
        color: #173f5f;
    }

    .disclaimer {
        background: #f1f1f1;
        padding: 15px;
        border-radius: 8px;
        font-size: 13px;
        color: #555;
        line-height: 1.6;
    }

    img {
        max-width: 100%;
        max-height: 400px;
        border-radius: 10px;
        display: block;
        margin: 15px auto;
        object-fit: contain;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }

    input,
    select {
        width: 100%;
        padding: 10px;
        margin-top: 5px;
        margin-bottom: 15px;
        box-sizing: border-box;
        border: 1px solid #ccc;
        border-radius: 6px;
    }

    button {
        background: #173f5f;
        color: white;
        border: none;
        padding: 12px 22px;
        border-radius: 7px;
        cursor: pointer;
        font-size: 16px;
    }

    button:hover {
        background: #0f2d43;
    }

    .small-note {
        font-size: 13px;
        color: #666;
        line-height: 1.5;
    }

    .section-note {
        color: #666;
        line-height: 1.6;
    }

    .capability {
        background: #f7f9fc;
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
    }

    .capability strong {
        color: #173f5f;
    }

    @media(max-width: 650px) {

        .grid {
            grid-template-columns: 1fr;
        }

        body {
            padding: 15px;
        }

    }

</style>
"""


# =========================================================
# PAGE START
# =========================================================

def page_start(title="Poshan AI"):

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>{title}</title>

        {HTML_STYLE}

    </head>

    <body>

    <div class="container">
    """


# =========================================================
# PAGE END
# =========================================================

def page_end():

    return """
    </div>

    </body>

    </html>
    """


# =========================================================
# HOME PAGE
# =========================================================

def home_page():

    return page_start(
        "Poshan AI - Screening"
    ) + """

    <div class="header">

        <h1>
            Poshan AI
        </h1>

        <p>
            AI-Assisted Child Nutrition Screening
        </p>

    </div>


    <div class="card">

        <h2>
            Child Assessment
        </h2>

        <p class="section-note">

            Enter the child's basic information and
            upload an image for AI-assisted screening.

        </p>


        <form method="POST"
              enctype="multipart/form-data">


            <label>
                Age (years)
            </label>

            <input
                type="number"
                name="age"
                step="0.1"
                min="0"
                max="19"
                required
            >


            <label>
                Sex
            </label>

            <select
                name="sex"
                required
            >

                <option value="female">
                    Female
                </option>

                <option value="male">
                    Male
                </option>

            </select>


            <label>
                Height (cm)
            </label>

            <input
                type="number"
                name="height"
                step="0.1"
                min="1"
                required
            >


            <label>
                Weight (kg)
            </label>

            <input
                type="number"
                name="weight"
                step="0.1"
                min="0.1"
                required
            >


            <label>
                Child Image
            </label>

            <input
                type="file"
                name="image"
                accept="image/*"
                required
            >


            <button type="submit">
                Analyze Child
            </button>


        </form>

    </div>


    <div class="disclaimer">

        <strong>
            Important:
        </strong>

        This system provides AI-assisted nutritional
        screening support and does not provide a
        medical diagnosis.

    </div>

    """ + page_end()


# =========================================================
# REQUEST HANDLER
# =========================================================

class PoshanHandler(BaseHTTPRequestHandler):


    # =====================================================
    # SEND HTML
    # =====================================================

    def send_html(self, content):

        content_bytes = content.encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(content_bytes))
        )

        self.end_headers()

        self.wfile.write(
            content_bytes
        )


    # =====================================================
    # GET REQUEST
    # =====================================================

    def do_GET(self):

        # -------------------------------------------------
        # Serve uploaded image
        # -------------------------------------------------

        if self.path == "/uploaded-image":

            image_path = getattr(
                self.server,
                "uploaded_image_path",
                None
            )

            if (
                not image_path
                or not Path(image_path).exists()
            ):

                self.send_response(
                    404
                )

                self.end_headers()

                return


            image_data = Path(
                image_path
            ).read_bytes()


            suffix = Path(
                image_path
            ).suffix.lower()


            if suffix in [
                ".jpg",
                ".jpeg"
            ]:

                content_type = "image/jpeg"

            elif suffix == ".png":

                content_type = "image/png"

            elif suffix == ".gif":

                content_type = "image/gif"

            elif suffix == ".webp":

                content_type = "image/webp"

            else:

                content_type = (
                    "application/octet-stream"
                )


            self.send_response(
                200
            )

            self.send_header(
                "Content-Type",
                content_type
            )

            self.send_header(
                "Content-Length",
                str(len(image_data))
            )

            self.end_headers()

            self.wfile.write(
                image_data
            )

            return


        # -------------------------------------------------
        # Normal home page
        # -------------------------------------------------

        self.send_html(
            home_page()
        )


    # =====================================================
    # POST REQUEST
    # =====================================================

    def do_POST(self):

        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )


            body = self.rfile.read(
                content_length
            )


            # ------------------------------------------------
            # Check multipart form
            # ------------------------------------------------

            content_type = self.headers.get(
                "Content-Type",
                ""
            )


            if "multipart/form-data" not in content_type:

                self.send_html(

                    page_start()

                    +

                    """
                    <div class="card">

                        <h2>
                            Invalid form submission.
                        </h2>

                    </div>
                    """

                    +

                    page_end()

                )

                return


            # ------------------------------------------------
            # Boundary
            # ------------------------------------------------

            boundary = content_type.split(
                "boundary="
            )[-1]

            boundary = boundary.encode()


            parts = body.split(
                b"--" + boundary
            )


            fields = {}

            uploaded_image = None

            uploaded_filename = None


            # ------------------------------------------------
            # Read form parts
            # ------------------------------------------------

            for part in parts:

                if (
                    b"Content-Disposition"
                    not in part
                ):

                    continue


                header_body = part.split(
                    b"\r\n\r\n",
                    1
                )


                if len(header_body) != 2:

                    continue


                headers = header_body[
                    0
                ].decode(
                    "utf-8",
                    errors="ignore"
                )


                data = header_body[
                    1
                ]


                data = data.rstrip(
                    b"\r\n-"
                )


                # =========================================
                # IMAGE
                # =========================================

                if 'name="image"' in headers:

                    filename_marker = (
                        'filename="'
                    )


                    if filename_marker in headers:

                        filename_start = (

                            headers.find(
                                filename_marker
                            )

                            +

                            len(filename_marker)

                        )


                        filename_end = headers.find(
                            '"',
                            filename_start
                        )


                        uploaded_filename = (
                            headers[
                                filename_start:
                                filename_end
                            ]
                        )


                    uploaded_image = data


                # =========================================
                # NORMAL FORM FIELD
                # =========================================

                else:

                    name_marker = 'name="'


                    if name_marker in headers:

                        name_start = (

                            headers.find(
                                name_marker
                            )

                            +

                            len(name_marker)

                        )


                        name_end = headers.find(
                            '"',
                            name_start
                        )


                        field_name = headers[
                            name_start:
                            name_end
                        ]


                        fields[field_name] = (
                            data.decode(
                                "utf-8",
                                errors="ignore"
                            ).strip()
                        )


            # =================================================
            # READ VALUES
            # =================================================

            age = float(
                fields.get(
                    "age",
                    0
                )
            )


            sex = fields.get(
                "sex",
                "female"
            )


            height = float(
                fields.get(
                    "height",
                    0
                )
            )


            weight = float(
                fields.get(
                    "weight",
                    0
                )
            )


            if uploaded_image is None:

                raise ValueError(
                    "Please upload a child image."
                )


            # =================================================
            # SAVE IMAGE TEMPORARILY
            # =================================================

            suffix = Path(
                uploaded_filename
                or
                "child.jpeg"
            ).suffix


            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:

                temp_file.write(
                    uploaded_image
                )

                temp_image_path = (
                    temp_file.name
                )


            # =================================================
            # RUN PERSON 4 ANALYSIS
            # =================================================

            result = analyze_child(

                age=age,

                sex=sex,

                height=height,

                weight=weight,

                image_path=temp_image_path

            )


            # =================================================
            # CREATE FRONTEND SUMMARY
            # =================================================

            summary = create_screening_summary(
                result
            )


            # =================================================
            # SAVE IMAGE PATH
            # =================================================

            self.server.uploaded_image_path = (
                temp_image_path
            )


            # =================================================
            # BUILD RESULT PAGE
            # =================================================

            result_page = build_result_page(

                summary,

                uploaded_filename,

                temp_image_path

            )


            self.send_html(
                result_page
            )


        except Exception as error:

            error_page = (

                page_start(
                    "Poshan AI - Error"
                )

                +

                f"""

                <div class="header">

                    <h1>
                        Poshan AI
                    </h1>

                </div>


                <div class="card">

                    <h2>
                        Unable to process the assessment
                    </h2>


                    <p>
                        {html.escape(
                            str(error)
                        )}
                    </p>


                    <br>


                    <a href="/">

                        <button>
                            Try Again
                        </button>

                    </a>

                </div>

                """

                +

                page_end()

            )


            self.send_html(
                error_page
            )


# =========================================================
# RESULT PAGE
# =========================================================

def build_result_page(
    summary,
    uploaded_filename,
    image_path
):

    child = summary[
        "child"
    ]


    growth = summary[
        "growth_screening"
    ]


    image = summary[
        "image_screening"
    ]


    vision = summary.get(
        "computer_vision_features",
        {}
    )


    capabilities = summary.get(
        "system_capabilities",
        {}
    )


    overall_status = summary[
        "overall_status"
    ]


    # =====================================================
    # FORMAT VALUES
    # =====================================================

    height_band = str(
        growth.get(
            "height_reference_band",
            "Not available"
        )
    ).replace(
        "between_",
        "Between "
    ).replace(
        "_and_",
        " and "
    ).replace(
        "_SD",
        " SD"
    )


    weight_band = str(
        growth.get(
            "weight_reference_band",
            "Not available"
        )
    ).replace(
        "between_",
        "Between "
    ).replace(
        "_and_",
        " and "
    ).replace(
        "_SD",
        " SD"
    )


    priority = str(
        growth.get(
            "screening_priority",
            "Not available"
        )
    ).replace(
        "_",
        " "
    ).title()


    display_status = str(
        overall_status
    ).replace(
        "_",
        " "
    ).upper()


    image_quality = str(
        image.get(
            "image_quality",
            "Unknown"
        )
    ).title()


    lighting = str(
        image.get(
            "lighting_uniformity",
            "Unknown"
        )
    ).title()


    color_information = str(
        image.get(
            "color_information",
            "Unknown"
        )
    ).title()


    image_name = html.escape(

        uploaded_filename
        or
        "Uploaded image"

    )


    # =====================================================
    # QUALITY ISSUES
    # =====================================================

    quality_issues = image.get(
        "quality_issues",
        []
    )


    if quality_issues:

        quality_issue_text = html.escape(

            ", ".join(
                quality_issues
            )

        )

    else:

        quality_issue_text = "None"


    # =====================================================
    # SYSTEM CAPABILITY VALUES
    # =====================================================

    image_quality_available = (
        "Available"
        if capabilities.get(
            "image_quality_analysis",
            False
        )
        else
        "Not available"
    )


    who_growth_available = (
        "Available"
        if capabilities.get(
            "who_growth_reference",
            False
        )
        else
        "Not available"
    )


    medical_ai_available = (
        "Connected"
        if capabilities.get(
            "medical_visual_ai",
            False
        )
        else
        "Not connected"
    )


    # =====================================================
    # RESULT PAGE
    # =====================================================

    return page_start(
        "Poshan AI - Screening Result"
    ) + f"""

    <!-- ============================================
         HEADER
         ============================================ -->

    <div class="header">

        <h1>
            Poshan AI
        </h1>

        <p>
            AI-Assisted Child Nutrition Screening
        </p>

    </div>


    <!-- ============================================
         CHILD PROFILE
         ============================================ -->

    <div class="card">

        <h2>
            Child Profile
        </h2>


        <div class="grid">


            <div class="item">

                <div class="label">
                    Age
                </div>

                <div class="value">
                    {child["age"]} years
                </div>

            </div>


            <div class="item">

                <div class="label">
                    Sex
                </div>

                <div class="value">

                    {
                        html.escape(
                            str(
                                child["sex"]
                            )
                        ).title()
                    }

                </div>

            </div>


            <div class="item">

                <div class="label">
                    Height
                </div>

                <div class="value">
                    {child["height_cm"]} cm
                </div>

            </div>


            <div class="item">

                <div class="label">
                    Weight
                </div>

                <div class="value">
                    {child["weight_kg"]} kg
                </div>

            </div>


        </div>

    </div>


    <!-- ============================================
         GROWTH SCREENING
         ============================================ -->

    <div class="card">

        <h2>
            Growth Screening
        </h2>


        <div class="grid">


            <div class="item">

                <div class="label">
                    Age
                </div>

                <div class="value neutral">

                    {
                        growth.get(
                            "age_months",
                            "N/A"
                        )
                    }

                    months

                </div>

            </div>


            <div class="item">

                <div class="label">
                    Screening Priority
                </div>

                <div class="value warning">

                    {html.escape(priority)}

                </div>

            </div>


            <div class="item">

                <div class="label">
                    Height Reference Band
                </div>

                <div class="value">

                    {html.escape(height_band)}

                </div>

            </div>


            <div class="item">

                <div class="label">
                    Weight Reference Band
                </div>

                <div class="value">

                    {html.escape(weight_band)}

                </div>

            </div>


        </div>


        <p class="section-note">

            {
                html.escape(
                    str(
                        growth.get(
                            "message",
                            "Growth screening information available."
                        )
                    )
                )
            }

        </p>


        <p>

            Reference:

            <strong>
                {html.escape(
                    str(
                        summary.get(
                            "reference",
                            "WHO Child Growth Standards"
                        )
                    )
                )}
            </strong>

        </p>


    </div>


    <!-- ============================================
         COMPUTER VISION / IMAGE SCREENING
         ============================================ -->

    <div class="card">

        <h2>
            Computer Vision / Image Screening
        </h2>


        <p>

            <strong>
                Input Image:
            </strong>

            {image_name}

        </p>


        <div class="grid">


            <!-- IMAGE QUALITY -->

            <div class="item">

                <div class="label">
                    Image Quality
                </div>

                <div class="value good">

                    {html.escape(image_quality)}

                </div>

            </div>


            <!-- RESOLUTION -->

            <div class="item">

                <div class="label">
                    Resolution
                </div>

                <div class="value">

                    {
                        image.get(
                            "image_width",
                            "N/A"
                        )
                    }

                    ×

                    {
                        image.get(
                            "image_height",
                            "N/A"
                        )
                    }

                </div>

            </div>


            <!-- BRIGHTNESS -->

            <div class="item">

                <div class="label">
                    Brightness
                </div>

                <div class="value">

                    {
                        image.get(
                            "brightness",
                            "N/A"
                        )
                    }

                </div>

            </div>


            <!-- CONTRAST -->

            <div class="item">

                <div class="label">
                    Contrast
                </div>

                <div class="value">

                    {
                        image.get(
                            "contrast",
                            "N/A"
                        )
                    }

                </div>

            </div>


            <!-- CLARITY -->

            <div class="item">

                <div class="label">
                    Clarity
                </div>

                <div class="value">

                    {
                        image.get(
                            "clarity",
                            "N/A"
                        )
                    }

                </div>

            </div>


            <!-- LIGHTING -->

            <div class="item">

                <div class="label">
                    Lighting Uniformity
                </div>

                <div class="value">

                    {html.escape(lighting)}

                </div>

            </div>


            <!-- COLOR INFORMATION -->

            <div class="item">

                <div class="label">
                    Color Information
                </div>

                <div class="value">

                    {html.escape(color_information)}

                </div>

            </div>


            <!-- COLORFULNESS -->

            <div class="item">

                <div class="label">
                    Colorfulness Score
                </div>

                <div class="value">

                    {
                        image.get(
                            "colorfulness_score",
                            "N/A"
                        )
                    }

                </div>

            </div>


            <!-- QUALITY ISSUES -->

            <div class="item">

                <div class="label">
                    Quality Issues
                </div>

                <div class="value">

                    {quality_issue_text}

                </div>

            </div>


        </div>


        <p class="small-note">

            These image-quality metrics are technical
            screening heuristics used to determine whether
            the uploaded image is suitable for further
            processing. They are not medical indicators.

        </p>


    </div>


    <!-- ============================================
         COMPUTER VISION FEATURES
         ============================================ -->

    <div class="card">

        <h2>
            Computer Vision Features
        </h2>


        <div class="grid">


            <div class="item">

                <div class="label">
                    Red Channel Mean
                </div>

                <div class="value">

                    {
                        vision.get(
                            "red_mean",
                            "N/A"
                        )
                    }

                </div>

            </div>


            <div class="item">

                <div class="label">
                    Green Channel Mean
                </div>

                <div class="value">

                    {
                        vision.get(
                            "green_mean",
                            "N/A"
                        )
                    }

                </div>

            </div>


            <div class="item">

                <div class="label">
                    Blue Channel Mean
                </div>

                <div class="value">

                    {
                        vision.get(
                            "blue_mean",
                            "N/A"
                        )
                    }

                </div>

            </div>


            <div class="item">

                <div class="label">
                    Pallor Indicator
                </div>

                <div class="value">

                    {
                        html.escape(
                            str(
                                vision.get(
                                    "pallor_indicator",
                                    "Not assessed"
                                )
                            ).replace(
                                "_",
                                " "
                            ).title()
                        )
                    }

                </div>

            </div>


            <div class="item">

                <div class="label">
                    Rib Prominence
                </div>

                <div class="value">

                    {
                        html.escape(
                            str(
                                vision.get(
                                    "rib_prominence",
                                    "Not assessed"
                                )
                            ).replace(
                                "_",
                                " "
                            ).title()
                        )
                    }

                </div>

            </div>


            <div class="item">

                <div class="label">
                    General Appearance
                </div>

                <div class="value">

                    {
                        html.escape(
                            str(
                                vision.get(
                                    "general_appearance",
                                    "Not assessed"
                                )
                            ).replace(
                                "_",
                                " "
                            ).title()
                        )
                    }

                </div>

            </div>


        </div>


        <p class="small-note">

            Medical visual indicators are currently not
            automatically classified. The current module
            performs image-quality and computer-vision
            feature analysis only.

        </p>


    </div>


    <!-- ============================================
         OVERALL SCREENING STATUS
         ============================================ -->

    <div class="card">

        <h2>
            Overall Screening Status
        </h2>


        <div class="status">

            🟡 {html.escape(display_status)}

        </div>


        <p class="section-note">

            The current screening status combines
            available growth-reference screening and
            image-quality analysis.

            It is a screening priority and does not
            represent a medical diagnosis.

        </p>


    </div>


    <!-- ============================================
         SYSTEM CAPABILITIES
         ============================================ -->

    <div class="card">

        <h2>
            System Capabilities
        </h2>


        <div class="capability">

            <strong>
                Image Quality Analysis:
            </strong>

            {image_quality_available}

        </div>


        <div class="capability">

            <strong>
                WHO Growth Reference:
            </strong>

            {who_growth_available}

        </div>


        <div class="capability">

            <strong>
                Medical Visual AI:
            </strong>

            {medical_ai_available}

        </div>


        <p class="small-note">

            Medical visual AI is intentionally shown as
            unavailable until a validated visual model
            is connected.

        </p>


    </div>


    <!-- ============================================
         COMPUTER VISION INPUT IMAGE
         ============================================ -->

    <div class="card">

        <h2>
            Computer Vision Input
        </h2>


        <p>

            <strong>
                Uploaded Image:
            </strong>

            {image_name}

        </p>


        <img
            src="/uploaded-image"
            alt="Uploaded child image"
        >


        <p class="small-note">

            The uploaded image was successfully
            received and processed by the screening
            module.

        </p>


    </div>


    <!-- ============================================
         MEDICAL DISCLAIMER
         ============================================ -->

    <div class="disclaimer">

        <strong>
            Medical Disclaimer:
        </strong>

        <br><br>

        {html.escape(
            str(
                summary.get(
                    "disclaimer",
                    "This is an AI-assisted screening result, not a medical diagnosis."
                )
            )
        )}

    </div>


    <br>


    <a href="/">

        <button>
            ← Analyze Another Child
        </button>

    </a>


    """ + page_end()


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    server = HTTPServer(
        (HOST, PORT),
        PoshanHandler
    )


    print(
        "\n========================================"
    )


    print(
        "             POSHAN AI DEMO"
    )


    print(
        "========================================"
    )


    print(
        "Open this in your browser:"
    )


    print(
        f"http://{HOST}:{PORT}"
    )


    print(
        "========================================\n"
    )


    try:

        server.serve_forever()


    except KeyboardInterrupt:

        print(
            "\nServer stopped."
        )


    finally:

        server.server_close()