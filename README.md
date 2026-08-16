🇫🇷 [Version française](README.fr.md)
# Insect Identification API

A REST API built with FastAPI that uses Claude's vision capabilities (Anthropic API) to automatically identify insects or pests from an image, returning structured information: species name, threat level, and recommended control methods.

## Context :
During an internship, developed by me for the backend of a mobile application meant to identify pests


## Features

- Image analysis via URL or base64-encoded image
- Species identification (common name + scientific name)
- Human threat level assessment (0.1–1.0 scale + label: low / moderate / high / critical)
- Suggested control methods and products
- Strict file type and size validation (max 5 MB, JPEG/PNG/GIF/WebP)
- Robust error handling (Claude timeout, rate limiting, malformed JSON, invalid image)
- Structured, validated responses using Pydantic

## Tech stack

- Python 3 / FastAPI
- Anthropic API (Claude, vision)
- Pydantic for data validation
- httpx for downloading remote images
- Docker for deployment

## Local setup

```bash
# Clone the repo
git clone https://github.com/Yonkeu-Onyx/Claude_Insect_Identification_api.git
cd Claude_Insect_Identification_api

# Install dependencies
pip install -r requirements.txt

# Configure the API key (see .env.example)
cp .env.example .env
# then add your ANTHROPIC_API_KEY in .env

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive auto-generated docs at `http://localhost:8000/docs`.

## Usage

POST `/claude_analyze`

```json body example for quick testing
{
  "image_url": "https://example.com/insect.jpg"
}
```

or with a base64-encoded image:

```json
{
  "image_url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

Response:

```json
{
  "success": true,
  "data": [
    {
      "common_name": "Asian lady beetle",
      "scientific_name": "Harmonia axyridis",
      "description": "...",
      "threat": 0.2,
      "label": "low",
      "control": "...",
      "produits": ["..."]
    }
  ]
}
```

## What I learned building this

- Using An AI's API endpoints effectively
- Integrating the use of an AI directly into an application
- Structuring a prompt to reliably force Claude to return strictly parsable JSON
- Validating and securing an image upload pipeline (MIME type, max size, base64 decoding)
- Handling errors from a third-party API properly (rate limits, timeouts, status errors) instead of relying on a generic `try/except`