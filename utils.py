import os
from PIL import Image, ImageFilter
import torch
from diffusers import (
    StableDiffusionXLImg2ImgPipeline,
    StableDiffusionXLControlNetPipeline,
    StableDiffusionXLRefinerPipeline,
    ControlNetModel,
    AutoencoderKL
)
from transformers import AutoTokenizer

# Load base SDXL pipeline
base_pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    variant="fp16" if torch.cuda.is_available() else None,
    use_safetensors=True
).to("cuda" if torch.cuda.is_available() else "cpu")

# Load SDXL Refiner
refiner = StableDiffusionXLRefinerPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-refiner-1.0",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    variant="fp16" if torch.cuda.is_available() else None,
    use_safetensors=True
).to("cuda" if torch.cuda.is_available() else "cpu")

# Dynamic ControlNet loader
def load_controlnet(control_type):
    model_map = {
        "canny": "diffusers/controlnet-canny-sdxl-1.0",
        "depth": "diffusers/controlnet-depth-sdxl-1.0",
        "pose": "diffusers/controlnet-openpose-sdxl-1.0",
        "seg": "diffusers/controlnet-seg-sdxl-1.0"
    }
    model_id = model_map.get(control_type, model_map["canny"])
    return ControlNetModel.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    ).to("cuda" if torch.cuda.is_available() else "cpu")

# Main filter function
def apply_filter(input_path, output_dir, filter_name, prompt=None, control_path=None, control_type=None):
    try:
        with Image.open(input_path) as img:
            if filter_name == 'ai':
                if not prompt:
                    return []

                img = img.convert("RGB").resize((1024, 1024))
                control_img = None

                if control_path and os.path.exists(control_path):
                    control_img = Image.open(control_path).convert("RGB").resize((1024, 1024))
                    controlnet_model = load_controlnet(control_type)

                    control_pipe = StableDiffusionXLControlNetPipeline(
                        vae=AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16),
                        controlnet=controlnet_model,
                        tokenizer=base_pipe.tokenizer,
                        text_encoder=base_pipe.text_encoder,
                        unet=base_pipe.unet,
                        scheduler=base_pipe.scheduler,
                        safety_checker=None,
                        feature_extractor=None,
                        requires_safety_checker=False,
                        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                    ).to("cuda" if torch.cuda.is_available() else "cpu")

                    base_images = control_pipe(
                        prompt=prompt,
                        image=img,
                        control_image=control_img,
                        strength=0.6,
                        guidance_scale=7.5,
                        num_images_per_prompt=3
                    ).images
                else:
                    base_images = base_pipe(
                        prompt=prompt,
                        image=img,
                        strength=0.6,
                        guidance_scale=7.5,
                        num_images_per_prompt=3
                    ).images

                output_files = []
                for i, base in enumerate(base_images):
                    refined = refiner(
                        prompt=prompt,
                        image=base,
                        strength=0.3,
                        guidance_scale=7.5
                    ).images[0]
                    filename = f"ai_{i}_{os.path.basename(input_path)}"
                    out_path = os.path.join(output_dir, filename)
                    refined.save(out_path)
                    output_files.append(filename)

                return output_files

            else:
                img = img.convert('RGB')
                if filter_name == 'grayscale':
                    img = img.convert('L')
                elif filter_name == 'blur':
                    img = img.filter(ImageFilter.BLUR)
                elif filter_name == 'contour':
                    img = img.filter(ImageFilter.CONTOUR)
                elif filter_name == 'sharpen':
                    img = img.filter(ImageFilter.SHARPEN)
                else:
                    return []

                filename = f"{filter_name}_{os.path.basename(input_path)}"
                out_path = os.path.join(output_dir, filename)
                img.save(out_path)
                return [filename]
    except Exception as e:
        print("Error:", e)
        return []