from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ASPECT_TO_SIZE = {
    "1:1": "1024x1024",
    "4:3": "1024x768",
    "16:9": "1280x720"
}

@app.post("/generate")
async def generate_image(
    prompt: str = Form(...),
    model: str = Form("Max"),
    aspect_ratio: str = Form("1:1"),
    outputs: int = Form(1),
    image: UploadFile = File(None)
):
    size = ASPECT_TO_SIZE.get(aspect_ratio, "1024x1024")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = { "prompt": prompt, "n": outputs, "size": size }
    url = "https://api.openai.com/v1/images/generations"

    # Note: This endpoint is text-to-image. If an image is uploaded, we currently ignore it
    # but return a hint. Proper img2img can be wired to a variations/edits endpoint later.
    hint = None
    if image is not None:
        hint = "Note: Uploaded image received. Current model uses text-to-image; img2img will be enabled in the next update."

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            return {
                "error": resp.text,
                "hint": hint
            }

        data = resp.json()
        images = [item["url"] for item in data.get("data", [])]
        return {
            "images": images,
            "hint": hint
        }
    except requests.RequestException as e:
        return { "error": f"Network error: {e}", "hint": hint }
