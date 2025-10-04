# 📘 FLEXBONE AI - CloudVision OCR API

### **Serverless Image Text Extraction API using Google Cloud Vision + Cloud Run**

A Flask-based REST API that extracts text from images using **Google Cloud Vision OCR**.
It supports **single and batch image uploads**, validates files securely, and returns structured JSON responses.
Deployed as a **serverless container** on **Google Cloud Run**.

---

## 🚀 Features

✅ Extract text from uploaded images using **Google Cloud Vision API**
✅ Supports multiple formats — **JPG, JPEG, PNG, GIF, WEBP**
✅ **Batch processing** endpoint for multiple files
✅ Returns **confidence score**, **processing time**, and **image metadata**
✅ Strict **file size (10MB)** and **rate limiting (5/min per IP)**
✅ Built with **Flask + Flask-RESTX** for Swagger documentation (`/docs`)
✅ Deployed on **Google Cloud Run** with **Docker** containerization
✅ Includes **automated tests** using `pytest` and `unittest.mock`
✅ **Automated CI/CD Pipeline** — Uses GitHub Actions to automatically build Docker images, push them to Google Artifact Registry, and deploy the latest version to Google Cloud Run on every push to `main`.

---

## 🧠 System Architecture

```
Client → Flask REST API → OCRService (Google Vision API) → JSON Response
```

---

## 🧩 API Documentation

### 🔹 Base URL

```
https://google-cloud-vision-api-with-gcr-dnpnqop5uq-wl.a.run.app/api
```

### Swagger UI (for batch process do not use swagger, use curl command instead)
```
https://google-cloud-vision-api-with-gcr-dnpnqop5uq-wl.a.run.app/docs
```
---

### **1️⃣ Extract Text from Single Image**

**Endpoint:**

```
POST /api/extract-text
```

**Description:**
Accepts one image and returns the extracted text, OCR confidence, and image metadata.

**Request Type:**
`multipart/form-data`

**Request Body Parameters:**

| Key     | Type | Required | Description                            |
| ------- | ---- | -------- | -------------------------------------- |
| `image` | File | ✅ Yes    | Image file (jpg, jpeg, png, gif, webp) |

**Example cURL Command:**

```bash
curl -X POST -F "image=@test_image.jpg" https://google-cloud-vision-api-with-gcr-dnpnqop5uq-wl.a.run.app/api/extract-text
```

**Example Successful Response:**

```json
{
  "success": true,
  "text": "Hello World from the image",
  "confidence": 0.95,
  "processing_time_ms": 340,
  "metadata": {
    "format": "JPEG",
    "mode": "RGB",
    "width": 1920,
    "height": 1080
  }
}
```

**Error Responses:**

| HTTP Code | Error                          | Description                                |
| --------- | ------------------------------ | ------------------------------------------ |
| `400`     | Invalid file type / Empty file | Uploaded file is unreadable or unsupported |
| `415`     | Invalid request type           | Must use multipart/form-data               |
| `413`     | File too large                 | Max 10MB limit                             |
| `500`     | Internal server error          | Vision API or OCR failure                  |

---

### **2️⃣ Extract Text from Multiple Images (Batch Processing)**

**Endpoint:**

```
POST /api/extract-text-batch
```

**Description:**
Upload multiple images and get text results concurrently (up to 10 threads).

**Request Type:**
`multipart/form-data`

**Request Body Parameters:**

| Key     | Type   | Required | Description          |
| ------- | ------ | -------- | -------------------- |
| `image` | File[] | ✅ Yes    | Multiple image files |

**Example cURL Command:**

```bash
curl -X POST \
  -F "image=@image1.jpg" \
  -F "image=@image2.png" \
  https://google-cloud-vision-api-with-gcr-dnpnqop5uq-wl.a.run.app/api/extract-text-batch
```

**Example Successful Response:**

```json
{
  "success": true,
  "results": [
    {
      "filename": "image1.jpg",
      "success": true,
      "text": "Hello",
      "confidence": 0.92,
      "processing_time_ms": 220,
      "metadata": {"format": "JPEG", "mode": "RGB", "width": 800, "height": 600}
    },
    {
      "filename": "image2.png",
      "success": true,
      "text": "World",
      "confidence": 0.88,
      "processing_time_ms": 300,
      "metadata": {"format": "PNG", "mode": "RGB", "width": 640, "height": 480}
    }
  ]
}
```

---

### **3️⃣ Health Check**

**Endpoint:**

```
GET /api/health
```

**Response:**

```json
{ "status": "healthy" }
```

---

## ⚙️ Implementation Details

### 🧩 OCR Engine

* **Google Cloud Vision API**
* Uses `document_text_detection` for accurate OCR on structured documents.
* Extracts `text`, `confidence`, and `metadata` (image format, size, mode).

### 🗂 File Upload & Validation

* Validates MIME type and file extension.
* Rejects empty or invalid files.
* Enforces 10MB size limit.

### 💡 Additional Enhancements

* **Batch OCR**: Uses `ThreadPoolExecutor` for parallel OCR calls.
* **Rate limiting**: `5 requests/min per IP` via Flask-Limiter.
* **Swagger UI**: Accessible at `/docs`.
* **Centralized error handling** via `utils/error_handler.py`.

---

## 🧪 Testing Instructions

### ✅ Run All Tests Locally

#### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2️⃣ Run Tests

```bash
pytest -v
```

#### 3️⃣ Example Output

```
tests/test_ocr.py::test_extract_text_success PASSED
tests/test_ocr.py::test_extract_text_batch_success PASSED
tests/test_ocr.py::test_health_check PASSED
```

#### 4️⃣ Test Coverage

Includes tests for:

* Valid image OCR
* Empty file upload
* Invalid file extensions
* Wrong MIME type
* Batch processing
* OCR runtime error simulation
* Health check endpoint

#### 5️⃣ Mocking

All OCR API calls are mocked (`unittest.mock.patch`) to avoid real Google Vision API usage during local tests.

---

## 🧰 Local Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/mr-teslaa/google-cloud-vision-api-with-gcr
cd google-cloud-vision-api-with-gcr
```

### 2️⃣ Create Environment File

Create a `.env` file:

```bash
GOOGLE_TYPE=xxxxx
GOOGLE_PROJECT_ID=xxx
GOOGLE_PRIVATE_KEY_ID=xxx
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nxxxx\n-----END PRIVATE KEY-----\n
GOOGLE_CLIENT_EMAIL=xxxx
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_X509_CERT_URL=xxx
```

### 3️⃣ Add Google Credentials
Download you service.json file and fill up the env placeholder with correct details from service.json

### 4️⃣ Run Locally

```bash
python run.py
```

Access locally: (for batch process do not use swagger, use curl command instead)
```
http://localhost:5000/docs
```

---

## ☁️ Deployment Guide (Google Cloud Run)

### 1️⃣ Build Docker Image
1. In your github repo go to Settings > Secrets > Actions
2. Create the following secrets there
```
GCP_PROJECT_ID
GCP_SA_KEY
GOOGLE_CLIENT_EMAIL
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_X509_CERT_URL
GOOGLE_PRIVATE_KEY
GOOGLE_PRIVATE_KEY_ID
GOOGLE_PROJECT_ID
GOOGLE_TYPE  
```

Push the code to you `main` branch and our `artifact-registry.yml` file will auto build the docker image and push it to google cloud artifact registry

### 2️⃣ Deploy to Cloud Run
1. When we push the code to `main` branch a docker image buld and auto pushed at google cloud artifact registry by using `artifact-registry.yml` 
2. Then the next github action will auto trigger `deploy.yml` and it will take the google authentication credentials from github secrets (i.e.GOOGLE_PRIVATE_KEY, GOOGLE_CLIENT_ID etc) and deploy it to google cloud directly

### 3️⃣ Get Your Public URL

Once deployed, Cloud Run provides a public endpoint like:

```
https://ocr-api-xyz.a.run.app
```

Test it:

```bash
curl -X POST -F "image=@test_image.jpg" https://ocr-api-xyz.a.run.app/api/extract-text
```

---

## 🧾 Project Structure

```
app/
|-- .github/workflows/.. # Github workflows for CI/CD pipeline auto docker image build and auto deploy to gcr
├── __init__.py          # Flask app factory + API + rate limiting
├── config.py            # Environment config + Google credentials validation
├── routes.py            # OCR endpoints
├── services/
│   └── ocr_service.py   # Vision OCR logic, text cleaning, metadata extraction
├── schemas/
│   ├── input.py         # API request schema
│   └── response.py      # API response schema
├── utils/
│   ├── file_utils.py    # File validation helpers
│   └── error_handler.py # Centralized error handlers
tests/
├── conftest.py          # Test fixtures
└── test_ocr.py          # Full unit + integration test coverage
run.py                   # App entrypoint
Dockerfile               # Cloud Run container config
requirements.txt         # Python dependencies
```

---

## 🧠 Key Design Decisions

* **App Factory Pattern** – Enables modular testing and scalability.
* **Flask-RESTX** – Provides automatic Swagger docs and validation.
* **ThreadPoolExecutor** – Parallel OCR for batch requests.
* **Error-First Design** – Centralized error handling ensures consistent responses.
* **Google Credentials Validation** – Dynamically verifies or generates credentials file at startup.

---

## 📸 Sample Test Images

Add a few images in `/samples/` folder for testing:

```
samples/
├── text_sample.jpg
├── blank_image.jpg
├── multiple_lines.jpg
```

---

## 🏁 Conclusion

This project demonstrates a **production-ready, scalable OCR API** built on **Google Cloud Run**.
It meets and exceeds all requirements — including batch processing, rich metadata, structured error handling, and test automation.

---

Would you like me to include a **“Dockerfile”** and **`requirements.txt`** section next (fully production-ready for Cloud Run)?
I can generate those immediately for you.
