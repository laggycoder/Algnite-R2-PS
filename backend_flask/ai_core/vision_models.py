# backend_flask/ai_core/vision_models.py
import os
import base64
from PIL import Image
import torch
from transformers import ViTImageProcessor, ViTModel
import openai as openai_sdk # Keep aliasing
from flask import current_app # To access app.logger and config

# --- ViT Model Loading (Moved here) ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
VIT_MODEL_NAME = 'google/vit-base-patch16-224-in21k'
image_processor_vit = None
vit_model_instance = None # Renamed to avoid conflict if vit_model is used as a var name

def load_vit_model():
    global image_processor_vit, vit_model_instance
    if image_processor_vit is None or vit_model_instance is None:
        try:
            current_app.logger.info(f"Loading ViT model: {VIT_MODEL_NAME} on device: {DEVICE}")
            image_processor_vit = ViTImageProcessor.from_pretrained(VIT_MODEL_NAME)
            vit_model_instance = ViTModel.from_pretrained(VIT_MODEL_NAME).to(DEVICE)
            vit_model_instance.eval()
            current_app.logger.info(f"Successfully loaded ViT model: {VIT_MODEL_NAME}")
        except Exception as e:
            current_app.logger.error(f"Error loading ViT model ({VIT_MODEL_NAME}): {e}. ViT features will be impaired.")
            image_processor_vit = None # Ensure they are None on failure
            vit_model_instance = None
    return image_processor_vit, vit_model_instance

def extract_vit_features(image_path_or_pil_image):
    processor, model = load_vit_model() # Ensure models are loaded
    if processor is None or model is None:
        current_app.logger.error("ViT model or processor not available for feature extraction.")
        return None
    try:
        if isinstance(image_path_or_pil_image, str):
            img = Image.open(image_path_or_pil_image).convert("RGB")
        else: # Assuming PIL Image
            img = image_path_or_pil_image.convert("RGB")

        inputs = processor(images=img, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            outputs = model(**inputs)
        features = outputs.last_hidden_state[:, 0, :].cpu().numpy() # CLS token
        return features.flatten()
    except Exception as e:
        current_app.logger.error(f"Error extracting ViT features: {e}")
        return None

def get_image_description_openai(image_path, openai_client_instance):
    if not openai_client_instance: # Check if client was successfully initialized in app.py
        current_app.logger.warning("OpenAI client not available. Skipping OpenAI Vision.")
        return "Image description not available (OpenAI client issue)."
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Determine image type (simple check, can be improved)
        image_type = "image/jpeg"
        if image_path.lower().endswith(".png"):
            image_type = "image/png"
        elif image_path.lower().endswith(".gif"):
            image_type = "image/gif"
        # Add more types if needed

        response = openai_client_instance.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image focusing on apparel, accessories, style, colors, patterns, material, occasion, and any notable features useful for e-commerce search. Provide a concise yet detailed summary. What kind of person might wear/use this? What other items might go well with it?"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{image_type};base64,{base64_image}"}
                        },
                    ],
                }
            ],
            max_tokens=350 # Increased for more detail including complementary ideas
        )
        description = response.choices[0].message.content
        current_app.logger.info(f"OpenAI Vision Description (snippet): {description[:100]}...")
        return description
    except openai_sdk.APIError as e:
        current_app.logger.error(f"OpenAI API Error in vision_models: Status {e.status_code} - {e.message}")
        return f"Error getting image description from OpenAI: API Error (Code: {e.status_code})"
    except Exception as e:
        current_app.logger.error(f"General error with OpenAI Vision API call in vision_models: {e}")
        return f"Error getting image description from OpenAI: {str(e)}"