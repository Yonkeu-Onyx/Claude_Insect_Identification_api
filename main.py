from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import anthropic
import base64
import os
from dotenv import load_dotenv
import re
import json
import httpx
import traceback


load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise Exception("Missing ANTHROPIC_API_KEY in .env")

client_claude = anthropic.Anthropic(api_key=API_KEY)

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_SIZE = 5 * 1024 * 1024  


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ImageRequest(BaseModel):
    image_url: str


class AnimalInfo(BaseModel):
    common_name: str
    scientific_name: str
    description: str
    threat: Optional[float] = None
    label: Optional[str] = None
    control: Optional[str] = None
    produits: Optional[List[str]] = None


class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[List[AnimalInfo]] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None


PROMPT = """
Pour l'image suivante, identifie l'animal qui s'y trouve, indique son nom scientifique 
et son nom commun, donne une très brève description de l'animal.

Sur une échelle de 0.1 à 1.0, indique le niveau de menace pour l'homme.
Ajoute un label: 'faible', 'modéré', 'élevé', 'critique'.

Propose une méthode de contrôle et quelques produits.

Retourne STRICTEMENT un JSON sous forme de tableau avec:
common_name, scientific_name, description, threat, label, control, produits

Si impossible, retourne []
"""


async def get_image_data(image_input: str) -> tuple[bytes, str]:
    
    if image_input.startswith("data:image"):
        try:
            header, b64_data = image_input.split(",", 1)

            
            match = re.match(r"data:(image/\w+);base64", header)
            if not match:
                raise HTTPException(400, "Invalid base64 image format")

            media_type = match.group(1)

            content = base64.b64decode(b64_data)

            return content, media_type

        except Exception as e:
            raise HTTPException(400, f"Invalid base64 image: {str(e)}")

    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_input)
    except Exception as e:
        raise HTTPException(400, f"Error downloading image: {str(e)}")

    if response.status_code != 200:
        raise HTTPException(400, "Failed to download image")

    media_type = response.headers.get("content-type", "").split(";")[0]

    if media_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {media_type}")

    content = response.content

    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large")

    return content, media_type


def encode_image(content: bytes) -> str:
    return base64.b64encode(content).decode()


def extract_text(message) -> str:
    text = ""
    for block in message.content:
        if hasattr(block, "text"):
            text += block.text
    return text


def clean_json(text: str) -> str:
    return re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()


def parse_json(text: str) -> list:
    parsed = json.loads(text)
    return [parsed] if isinstance(parsed, dict) else parsed



def call_claude(image_b64: str, media_type: str):
    return client_claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
    )


@app.post("/claude_analyze", response_model=AnalysisResponse)
async def analyze_image(req: ImageRequest):
    try:
        
        content, content_type = await get_image_data(req.image_url)

        
        image_b64 = encode_image(content)

        message = call_claude(image_b64, content_type)

        raw_text = extract_text(message)
        cleaned = clean_json(raw_text)

        parsed = parse_json(cleaned)

        return AnalysisResponse(
            success=True,
            data=parsed,
            raw_response=raw_text
        )

    except json.JSONDecodeError as e:
        return AnalysisResponse(
            success=False,
            error=f"Invalid JSON from Claude: {str(e)}",
            raw_response=raw_text if 'raw_text' in locals() else None
        )

    except anthropic.APIConnectionError as e:
        raise HTTPException(503, f"Claude connection error: {str(e)}")

    except anthropic.RateLimitError:
        raise HTTPException(429, "Rate limit exceeded")

    except anthropic.APIStatusError as e:
        raise HTTPException(e.status_code, f"Claude API error: {str(e)}")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
