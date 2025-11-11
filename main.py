from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests, os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/generate")
async def generate_image(
    prompt: str = Form(...),
    size: str = Form("1024x1024"),
    outputs: int = Form(1),
    images: list[UploadFile] = File(None)
):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    results = []

    try:
        if images:
            # ✅ Img2Img transformation for multiple images
            for img in images[:5]:  # max 5 images
                files = {"image": (img.filename, img.file, img.content_type)}
                data = {"prompt": prompt, "n": outputs, "size": size}
                resp = requests.post(
                    "https://api.openai.com/v1/images/edits",
                    headers=headers,
                    files=files,
                    data=data
                )
                if resp.status_code == 200:
                    data_json = resp.json()
                    urls = [item["url"] for item in data_json.get("data", [])]
                    results.append({"original": img.filename, "outputs": urls})
                else:
                    results.append({"original": img.filename, "error": resp.text})
        else:
            # ✅ Normal text-to-image
            payload = {"prompt": prompt, "n": outputs, "size": size}
            resp = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={**headers, "Content-Type": "application/json"},
                json=payload
            )
            if resp.status_code == 200:
                data_json = resp.json()
                urls = [item["url"] for item in data_json.get("data", [])]
                results.append({"original": None, "outputs": urls})
            else:
                results.append({"error": resp.text})

        return {"results": results}

    except requests.RequestException as e:
        return {"error": str(e)}
