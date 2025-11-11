from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests, os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

# ✅ CORS setup for Netlify frontend
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
    aspect: str = Form("1:1"),
    model: str = Form("max"),  # UI only
    images: list[UploadFile] = File(None)
):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    results = []

    n = min(max(int(outputs), 1), 4)  # Limit outputs to 1–4

    try:
        if images:
            # ✅ Image-to-Image transformation
            for img in images[:5]:
                files = {"image": (img.filename, img.file, img.content_type)}
                data = {"prompt": prompt, "n": n, "size": size}
                resp = requests.post(
                    "https://api.openai.com/v1/images/edits",
                    headers=headers,
                    files=files,
                    data=data
                )
                if resp.status_code == 200:
                    data_json = resp.json()
                    urls = [item.get("url") for item in data_json.get("data", []) if item.get("url")]
                    print(f"✅ Img2Img URLs for {img.filename}: {urls}")
                    results.append({"original": img.filename, "outputs": urls})
                else:
                    print(f"❌ Img2Img error for {img.filename}: {resp.text}")
                    results.append({"original": img.filename, "error": resp.text})
        else:
            # ✅ Text-to-Image generation
            payload = {"prompt": prompt, "n": n, "size": size}
            resp = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={**headers, "Content-Type": "application/json"},
                json=payload
            )
            if resp.status_code == 200:
                data_json = resp.json()
                urls = [item.get("url") for item in data_json.get("data", []) if item.get("url")]
                print(f"✅ Text2Img URLs: {urls}")
                results.append({"original": None, "outputs": urls})
            else:
                print(f"❌ Text2Img error: {resp.text}")
                results.append({"error": resp.text})

        return {"results": results}

    except requests.RequestException as e:
        print(f"❌ RequestException: {str(e)}")
        return {"error": str(e)}
