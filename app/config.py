import os, json, tempfile


class Config:
    GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service.json")

    @classmethod
    def validate_credentials(cls):
        creds_path = cls.GOOGLE_CREDENTIALS

        # If the env var itself contains JSON
        if creds_path.strip().startswith("{"):
            try:
                json.loads(creds_path)  # validate JSON
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
                tmp.write(creds_path.encode("utf-8"))
                tmp.flush()
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name
                return
            except Exception as e:
                raise RuntimeError("Invalid GOOGLE_APPLICATION_CREDENTIALS JSON") from e

        # Otherwise, fall back to file path
        if not os.path.isfile(creds_path):
            raise RuntimeError(
                f"❌ Google credentials file not found at '{creds_path}'"
            )
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path


# import os
# from dotenv import load_dotenv, find_dotenv

# load_dotenv(find_dotenv())


# class Config:
#     PORT = os.getenv("PORT", 5000)
#     MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
#     ALLOWED_EXTENSIONS = {"jpg", "jpeg"}
#     GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service.json")

#     @classmethod
#     def validate_credentials(cls):
#         """Validate that the Google credentials file exists and is readable."""
#         creds_path = cls.GOOGLE_CREDENTIALS

#         if not creds_path:
#             raise RuntimeError(
#                 "❌ GOOGLE_APPLICATION_CREDENTIALS not set in environment or .env file"
#             )

#         if not os.path.isfile(creds_path):
#             raise RuntimeError(
#                 f"❌ Google credentials file not found at '{creds_path}'. "
#                 "Check your .env file or default path."
#             )

#         if not creds_path.endswith(".json"):
#             raise RuntimeError(
#                 f"❌ Invalid credentials file: {creds_path}. Must be a .json file."
#             )

#         # If valid, export for Google SDK
#         os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
