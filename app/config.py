import os
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Config:
    PORT = os.getenv("PORT", 5000)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {"jpg", "jpeg"}
    GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service.json")

    @classmethod
    def validate_credentials(cls):
        """Ensure Google credentials are available either from env vars or file."""

        # Case 1: full service.json path is provided (works like before)
        creds_path = cls.GOOGLE_CREDENTIALS
        if os.path.isfile(creds_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
            return

        # Case 2: build JSON from env vars if file is missing
        required_vars = [
            "GOOGLE_TYPE",
            "GOOGLE_PROJECT_ID",
            "GOOGLE_PRIVATE_KEY_ID",
            "GOOGLE_PRIVATE_KEY",
            "GOOGLE_CLIENT_EMAIL",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_X509_CERT_URL",
        ]
        missing = [v for v in required_vars if not os.getenv(v)]
        if missing:
            raise RuntimeError(
                f"❌ Missing Google credential env vars: {', '.join(missing)} "
                f"and no service.json found at {creds_path}"
            )

        creds_dict = {
            "type": os.getenv("GOOGLE_TYPE"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
            "universe_domain": "googleapis.com",
        }

        # 👉 Trick: write it once as if it were the real service.json
        creds_file_path = "service.json"
        with open(creds_file_path, "w", encoding="utf-8") as f:
            json.dump(creds_dict, f, indent=2, ensure_ascii=False)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_file_path
        cls.GOOGLE_CREDENTIALS = creds_file_path
