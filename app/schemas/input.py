from flask_restx import fields


def register_input_schemas(api):
    OCRInputSchema = api.model(
        "OCRInput",
        {
            "image": fields.String(
                description="JPEG image file (multipart/form-data)", required=True
            )
        },
    )
    return OCRInputSchema
