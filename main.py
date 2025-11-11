from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_image(
    prompt: str = Form(...),
    model: str = Form("Max"),
    aspect_ratio: str = Form("1:1"),
    outputs: int = Form(1),
    image: UploadFile = File(None)
):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Aspect ratio mapping
    size_map = {
        "1:1": "1024x1024",
        "4:3": "1024x768",
        "16:9": "1280x720"
    }
    size = size_map.get(aspect_ratio, "1024x1024")

    payload = {
        "prompt": prompt,
        "n": outputs,
        "size": size
    }

    url = "https://api.openai.com/v1/images/generations"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        images = [img["url"] for img in data.get("data", [])]
        return {"images": images}
    else:
        return {"error": response.text}
