# 🖼️ p2i — Prompt-to-Image Transformer

A privacy-first, open-source image transformation tool powered by Stable Diffusion XL, Refiner, and ControlNet.

## 🔧 Features

- Prompt-based image-to-image transformation (SDXL)
- ControlNet support (Canny, Depth, Pose, Segmentation)
- SDXL Refiner for high-quality output
- Classic filters (grayscale, blur, sharpen, etc.)
- Frontend with:
  - Prompt suggestions
  - Control image upload + preview
  - Download buttons + Download All
  - History tab with Clear History
  - Theme toggle (Light/Dark)
  - Webcam capture

## 🚀 Deployment

### Local

```bash
pip install -r requirements.txt
python app.py