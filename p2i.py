from PIL import Image, ImageEnhance
import os

def p2i(prompt, image_path):
    try:
        img = Image.open(image_path)

        if "bright" in prompt.lower():
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.8)
        elif "rotate" in prompt.lower():
            img = img.rotate(45)
        elif "contrast" in prompt.lower():
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
        else:
            img = img.resize((img.width // 2, img.height // 2))

        output_filename = "output_" + os.path.basename(image_path)
        output_path = os.path.join("uploads", output_filename)
        img.save(output_path)

        return {
            "status": "success",
            "prompt": prompt,
            "input_image": image_path,
            "output_image": output_path
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }