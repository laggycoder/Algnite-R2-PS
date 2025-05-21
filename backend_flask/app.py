import os
import uuid
import json
import base64
import requests

from flask import Flask, request, jsonify, render_template, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import torch
from transformers import ViTImageProcessor, ViTModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from dotenv import load_dotenv
load_dotenv()

import openai as openai_sdk
import google.generativeai as genai

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join('static', 'product_images'), exist_ok=True) # Ensure product_images dir exists

# --- API Key Setup ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

openai_client = None
if not OPENAI_API_KEY:
    app.logger.warning("OPENAI_API_KEY not found. OpenAI features will be disabled.")
else:
    try:
        openai_client = openai_sdk.OpenAI(api_key=OPENAI_API_KEY)
        app.logger.info("OpenAI client initialized successfully.")
    except Exception as e:
        app.logger.error(f"Failed to initialize OpenAI client: {e}")

if not GOOGLE_API_KEY:
    app.logger.warning("GOOGLE_API_KEY not found. Gemini features will be disabled.")
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        app.logger.info("Google Generative AI configured successfully.")
    except Exception as e:
        app.logger.error(f"Failed to configure Google Generative AI: {e}")

# --- AI Model Loading (ViT) ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
app.logger.info(f"Using device for ViT: {DEVICE}")
VIT_MODEL_NAME = 'google/vit-base-patch16-224-in21k' # Corrected variable name
image_processor_vit = None
vit_model = None
try:
    image_processor_vit = ViTImageProcessor.from_pretrained(VIT_MODEL_NAME)
    vit_model = ViTModel.from_pretrained(VIT_MODEL_NAME).to(DEVICE)
    vit_model.eval()
    app.logger.info(f"Successfully loaded ViT model: {VIT_MODEL_NAME}")
except Exception as e:
    app.logger.error(f"Error loading ViT model ({VIT_MODEL_NAME}): {e}. ViT features will be impaired.")


# --- Product Database (IMPORTANT: Update 'image_path_for_ai' to your LOCAL images) ---
MOCK_PRODUCTS_DB = [
    {"id": "prod1", "name": "Classic Red Cotton T-Shirt", "price": "$19.99", "type": "T-Shirt", "category": "Apparel", "style": "Casual", "material": "Cotton", "color_tags": ["red", "solid"], "description": "A comfortable and stylish red t-shirt made from 100% cotton. Perfect for everyday wear.", "images": [f"https://via.placeholder.com/400x450/FF6347/FFFFFF?Text=RedTee1", f"https://via.placeholder.com/400x450/CD5C5C/FFFFFF?Text=RedTee2"], "image_path_for_ai": "static/product_images/red_tshirt.jpg", "sizes": ["S", "M", "L"], "colors": ["Red", "Dark Red"], "detailedReasons": ["Matches color 'Red'"], "embedding": None},
    {"id": "prod2", "name": "Blue Slim-Fit Denim Jeans", "price": "$49.99", "type": "Jeans", "category": "Apparel", "style": "Casual", "material": "Denim", "color_tags": ["blue", "denim"], "description": "Perfectly fitting blue slim-fit denim jeans. A wardrobe staple.", "images": [f"https://via.placeholder.com/400x450/1E90FF/FFFFFF?Text=BlueJeans1"], "image_path_for_ai": "static/product_images/blue_jeans.jpg", "sizes": ["28", "30", "32"], "colors": ["Blue"], "detailedReasons": ["Pairs with T-Shirts"], "embedding": None},
    {"id": "prod3", "name": "Stylish Grey Running Sneakers", "price": "$79.00", "type": "Sneakers", "category": "Footwear", "style": "Sporty", "material": "Mesh", "color_tags": ["grey", "black", "athletic"], "description": "Comfortable and trendy grey running sneakers with breathable mesh. Ideal for workouts or casual outings.", "images": [f"https://via.placeholder.com/400x450/D3D3D3/000000?Text=Sneakers1", f"https://via.placeholder.com/400x450/A9A9A9/FFFFFF?Text=Sneakers2"], "image_path_for_ai": "static/product_images/grey_sneakers.jpg", "sizes": ["8", "9", "10"], "colors": ["Grey", "Black"], "detailedReasons": ["Good for athletic wear"], "embedding": None},
    {"id": "prod4", "name": "Summer Floral Maxi Dress", "price": "$65.00", "type": "Dress", "category": "Apparel", "style": "Bohemian", "material": "Rayon", "color_tags": ["pink", "floral", "multi-color", "summer"], "description": "Light and airy floral maxi dress for summer, bohemian style. Features a vibrant floral print.", "images": [f"https://via.placeholder.com/400x450/FFC0CB/000000?Text=FloralDress1"], "image_path_for_ai": "static/product_images/floral_dress.jpg", "sizes": ["S", "M", "L"], "colors": ["Pink Floral"], "detailedReasons": ["Vibe: Summer", "Pattern: Floral"], "embedding": None},
    {"id": "prod5", "name": "Classic Brown Leather Belt", "price": "$25.00", "type": "Belt", "category": "Accessory", "style": "Classic", "material": "Leather", "color_tags": ["brown", "leather"], "description": "Classic brown genuine leather belt with a timeless buckle. Adds a polished touch to any outfit.", "images": [f"https://via.placeholder.com/400x450/8B4513/FFFFFF?Text=Belt1"], "image_path_for_ai": "static/product_images/leather_belt.jpg", "sizes": ["One Size"], "colors": ["Brown"], "detailedReasons": ["Accessory for Jeans"], "embedding": None},
    {"id": "prod6", "name": "Comfy Light Blue Hoodie", "price": "$55.99", "type": "Hoodie", "category": "Apparel", "style": "Casual", "material": "Fleece", "color_tags": ["blue", "light blue", "cozy"], "description": "A very comfortable light blue hoodie made of soft fleece. Features a kangaroo pocket and drawstring hood.", "images": [f"https://via.placeholder.com/400x450/B0C4DE/000000?Text=Hoodie1"], "image_path_for_ai": "static/product_images/blue_hoodie.jpg", "sizes": ["M", "L", "XL"], "colors": ["Light Blue"], "detailedReasons": ["Great for cool evenings"], "embedding": None}
]
AI_PRODUCT_DATABASE = []

# --- Helper & AI Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_vit_features(image_path_or_pil_image):
    if image_processor_vit is None or vit_model is None:
        app.logger.error("ViT model or processor not loaded. Cannot extract ViT features.")
        return None
    try:
        if isinstance(image_path_or_pil_image, str):
            img = Image.open(image_path_or_pil_image).convert("RGB")
        else:
            img = image_path_or_pil_image.convert("RGB")
        inputs = image_processor_vit(images=img, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            outputs = vit_model(**inputs)
        features = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        return features.flatten()
    except Exception as e:
        app.logger.error(f"Error extracting ViT features: {e}")
        return None

def get_image_description_openai(image_path):
    if not openai_client:
        app.logger.warning("OpenAI client not initialized. Skipping OpenAI Vision.")
        return "Image description not available (OpenAI Vision not configured/failed to init)."
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        response = openai_client.chat.completions.create(
            model="gpt-4o", # Updated model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image focusing on apparel, accessories, style, colors, patterns, material, occasion, and any notable features useful for e-commerce search. Provide a concise yet detailed summary."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        },
                    ],
                }
            ],
            max_tokens=300 # Increased for potentially more detail
        )
        description = response.choices[0].message.content
        app.logger.info(f"OpenAI Vision Description: {description[:100]}...") # Log snippet
        return description
    except openai_sdk.APIError as e: # Catch specific OpenAI errors
        app.logger.error(f"OpenAI API Error: {e.status_code} - {e.message}")
        return f"Error getting image description from OpenAI: {e.message} (Code: {e.status_code})"
    except Exception as e:
        app.logger.error(f"General error with OpenAI Vision API call: {e}")
        return f"Error getting image description from OpenAI: {str(e)}"

def get_refined_search_gemini(image_description, user_prompt, product_context_str=""):
    if not GOOGLE_API_KEY or not genai._configured: # Check if configured
        app.logger.warning("Google API Key not found or GenAI not configured. Skipping Gemini.")
        return {"error": "Gemini not configured."}
    try:
        gemini_model_name = "gemini-1.5-flash-latest" # Updated model
        model = genai.GenerativeModel(gemini_model_name)
        app.logger.info(f"Using Gemini model: {gemini_model_name}")
        
        prompt_template = f"""
        You are an AI shopping assistant helping a user find products.
        Image Context: "{image_description}"
        User's Query: "{user_prompt}"
        Optional Product Ideas (if any): "{product_context_str}"

        Based on all the above, provide a structured JSON response with the following keys:
        - "key_attributes": A list of 3-5 key attributes (e.g., "red dress", "leather handbag", "formal event", "cotton t-shirt", "summer vibe").
        - "suggested_search_terms": A list of 2-3 effective e-commerce search terms.
        - "catchy_phrase": A very short (1-2 sentence) engaging phrase describing the desired item or style.
        - "complementary_ideas": (Optional) A list of 1-2 types of complementary items, if obvious.

        Example Output:
        {{
          "key_attributes": ["casual", "t-shirt", "red", "cotton"],
          "suggested_search_terms": ["red cotton tee", "casual red top", "comfortable summer shirt"],
          "catchy_phrase": "Find your perfect red casual tee for sunny days!",
          "complementary_ideas": ["blue denim jeans", "white sneakers"]
        }}
        Ensure the output is valid JSON.
        """
        
        response = model.generate_content(prompt_template)
        
        # Try to parse Gemini's response as JSON
        try:
            cleaned_response_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            gemini_output = json.loads(cleaned_response_text)
            app.logger.info(f"Gemini Refinement Output: {gemini_output}")
            return gemini_output
        except json.JSONDecodeError:
            app.logger.warning(f"Gemini response was not valid JSON: {response.text}")
            return {"raw_text": response.text, "error": "Gemini response format issue. Returned raw text."}
        except Exception as e_parse: # Catch other parsing errors
            app.logger.error(f"Error parsing Gemini response: {e_parse}")
            return {"raw_text": response.text, "error": f"Gemini parsing error: {str(e_parse)}"}

    except Exception as e: # Catch errors from the API call itself
        app.logger.error(f"Error with Gemini API call: {e}")
        return {"error": f"Error interacting with Gemini: {str(e)}"}

def preprocess_product_database():
    global AI_PRODUCT_DATABASE
    AI_PRODUCT_DATABASE = []
    if not image_processor_vit or not vit_model:
        app.logger.error("ViT models not loaded. Cannot preprocess product database for ViT features.")
        # Populate AI_PRODUCT_DATABASE with no embeddings for text search
        for product_template in MOCK_PRODUCTS_DB:
            product = product_template.copy()
            product["embedding"] = None
            product["imageUrl"] = product.get("images")[0] if product.get("images") else "https://via.placeholder.com/260x250/CCCCCC/000000?Text=NoImg"
            AI_PRODUCT_DATABASE.append(product)
        app.logger.warning("AI_PRODUCT_DATABASE populated without ViT embeddings due to model load failure.")
        return

    app.logger.info("Preprocessing product database for ViT features...")
    processed_count = 0
    for product_template in MOCK_PRODUCTS_DB:
        product = product_template.copy()
        image_to_process_path = product.get('image_path_for_ai')

        if image_to_process_path and os.path.exists(image_to_process_path):
            embedding = extract_vit_features(image_to_process_path)
            if embedding is not None:
                product["embedding"] = embedding
                processed_count += 1
            else:
                product["embedding"] = None
                app.logger.warning(f"Failed to get ViT embedding for {product['name']} using path: {image_to_process_path}")
        else:
            product["embedding"] = None
            app.logger.warning(f"Product '{product['name']}' missing valid 'image_path_for_ai': {image_to_process_path}. Skipping ViT embedding.")
        
        product["imageUrl"] = product.get("images")[0] if product.get("images") else "https://via.placeholder.com/260x250/CCCCCC/000000?Text=NoImg"
        AI_PRODUCT_DATABASE.append(product)

    app.logger.info(f"Finished ViT preprocessing. {processed_count}/{len(MOCK_PRODUCTS_DB)} products have ViT embeddings.")
    if processed_count == 0 and len(MOCK_PRODUCTS_DB) > 0:
        app.logger.warning("No products were successfully embedded with ViT. Check image paths and ViT model loading.")


with app.app_context():
    preprocess_product_database()


def generate_final_recommendations(query_image_path=None, text_prompt="", top_k=10):
    openai_description = None
    gemini_refinement_data = None
    visual_recommendations = []

    if query_image_path:
        openai_description = get_image_description_openai(query_image_path)
        query_embedding = extract_vit_features(query_image_path)
        if query_embedding is not None and AI_PRODUCT_DATABASE:
            db_embeddings_tuples = [(p["embedding"], p) for p in AI_PRODUCT_DATABASE if p.get("embedding") is not None]
            if db_embeddings_tuples:
                db_embeddings = np.array([t[0] for t in db_embeddings_tuples])
                products_with_embeddings = [t[1] for t in db_embeddings_tuples]
                
                similarities = cosine_similarity(query_embedding.reshape(1, -1), db_embeddings)[0]
                sorted_indices = np.argsort(similarities)[::-1]

                for i in sorted_indices:
                    if len(visual_recommendations) < top_k * 2:
                        product = products_with_embeddings[i].copy()
                        similarity_score = float(similarities[i]) # Ensure it's float
                        product["recommendationReason"] = f"Visually similar (ViT Score: {similarity_score:.2f})"
                        product["detailedReasons"] = [f"ViT Similarity: {similarity_score:.2f}"]
                        product["visual_score"] = similarity_score # Store for later scoring
                        visual_recommendations.append(product)
            else:
                app.logger.warning("No product ViT embeddings in AI_PRODUCT_DATABASE for comparison.")
        elif not AI_PRODUCT_DATABASE:
             app.logger.warning("AI_PRODUCT_DATABASE is empty, cannot perform visual search.")
        else: # query_embedding is None
             app.logger.warning(f"Could not get ViT embedding for query image: {query_image_path}")


    current_desc_for_gemini = openai_description if openai_description and "Error" not in openai_description else "No specific visual input."
    if text_prompt or current_desc_for_gemini != "No specific visual input.":
        product_ctx_str = "Initial visual ideas: " + ", ".join([p['name'] for p in visual_recommendations[:3]]) if visual_recommendations else ""
        gemini_refinement_data = get_refined_search_gemini(current_desc_for_gemini, text_prompt, product_ctx_str)

    candidate_products = visual_recommendations if visual_recommendations else [p.copy() for p in AI_PRODUCT_DATABASE]
    if not candidate_products: # If AI_PRODUCT_DATABASE was empty too
        app.logger.info("No candidate products. Returning empty.")
        return [], openai_description, gemini_refinement_data

    scored_recommendations = []
    search_keywords = text_prompt.lower().split()
    if gemini_refinement_data and isinstance(gemini_refinement_data, dict) and not gemini_refinement_data.get("error"):
        if isinstance(gemini_refinement_data.get("suggested_search_terms"), list):
            search_keywords.extend([term.lower() for term in gemini_refinement_data["suggested_search_terms"]])
        elif isinstance(gemini_refinement_data.get("suggested_search_terms"), str):
             search_keywords.extend(gemini_refinement_data["suggested_search_terms"].lower().split())
        search_keywords = list(set(filter(None, search_keywords))) # Unique, non-empty keywords

    for product in candidate_products:
        score = product.get("visual_score", 0.0) * 10.0 # Weight visual score
        current_reasons = product.get("detailedReasons", [])
        
        text_match_count = 0
        product_text_corpus = (f"{product.get('name','')} {product.get('description','')} {product.get('type','')} "
                               f"{product.get('category','')} {product.get('style','')} {product.get('material','')} "
                               f"{' '.join(product.get('color_tags',[]))}").lower()
        
        matched_kw_for_this_product = []
        for kw in search_keywords:
            if kw in product_text_corpus:
                text_match_count += 1
                matched_kw_for_this_product.append(kw)
        
        score += text_match_count * 2.5 # Weight text matches

        if text_match_count > 0:
            reason_str = f"Matches keywords: {', '.join(matched_kw_for_this_product)}"
            current_reasons.append(reason_str)
            if "Visually similar" not in product.get("recommendationReason",""):
                 product["recommendationReason"] = reason_str
            else:
                 product["recommendationReason"] += f" & {reason_str.lower()}"
        
        product["final_score"] = score
        product["detailedReasons"] = current_reasons
        scored_recommendations.append(product)

    scored_recommendations.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    final_recommendations = scored_recommendations[:top_k]
    
    # Fallback if no recommendations scored high enough or list is empty
    if not final_recommendations and AI_PRODUCT_DATABASE:
        app.logger.info("No specific recommendations after scoring. Falling back to generic items.")
        final_recommendations = [p.copy() for i, p in enumerate(AI_PRODUCT_DATABASE) if i < top_k]
        for rec in final_recommendations: rec["recommendationReason"] = "Popular item (fallback)"


    for rec in final_recommendations: # Ensure imageUrl and update reason with score
        rec["imageUrl"] = rec.get("images")[0] if rec.get("images") else (rec.get("imageUrl") or "https://via.placeholder.com/260x250/CCCCCC/000000?Text=NoImg")
        base_reason = rec.get("recommendationReason", "Recommended")
        rec["recommendationReason"] = f"{base_reason} (Score: {rec.get('final_score', 0.0):.1f})"


    return final_recommendations, openai_description, gemini_refinement_data

# --- Routes ---
@app.route('/')
def index():
    initial_recs, _, _ = generate_final_recommendations(text_prompt="featured popular items", top_k=8)
    return render_template('index.html', initial_recommendations=json.dumps(initial_recs))

@app.route('/upload_image', methods=['POST'])
def upload_image_route():
    if 'imageFile' not in request.files:
        return jsonify({"error": "No image file part"}), 400
    file = request.files['imageFile']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            prompt_text = request.form.get('prompt', '') # Get prompt if sent with image
            
            recommendations, openai_desc, gemini_refine = generate_final_recommendations(
                query_image_path=filepath, text_prompt=prompt_text
            )
            
            # This URL is for the frontend to display the image it just uploaded
            image_url_for_preview = url_for('static', filename=f'../{UPLOAD_FOLDER}/{filename}')
            
            # For the hackathon, we won't delete filepath immediately so preview can work.
            # In a prod system, you'd manage this temporary file lifecycle carefully.

            return jsonify({
                "message": "Image processed",
                "filename_server_temp": filename,
                "image_preview_url": image_url_for_preview,
                "recommendations": recommendations,
                "openai_description": openai_desc,
                "gemini_refinement": gemini_refine
            })
        except Exception as e:
            app.logger.error(f"Error processing uploaded image route: {e}", exc_info=True)
            if os.path.exists(filepath): # Attempt to clean up on error
                try: os.remove(filepath)
                except: pass
            return jsonify({"error": f"Server error processing image: {str(e)}"}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations_route():
    data = request.json
    prompt_text = data.get('prompt', '')
    # This route is for text-only search or refinement where image is not newly uploaded.
    # The `generate_final_recommendations` will not have `query_image_path`
    try:
        recommendations, _, gemini_refine = generate_final_recommendations(text_prompt=prompt_text)
        return jsonify({
            "recommendations": recommendations,
            "gemini_refinement": gemini_refine 
        })
    except Exception as e:
        app.logger.error(f"Error getting text recommendations: {e}", exc_info=True)
        return jsonify({"error": "Failed to get recommendations"}), 500

@app.route('/mock_checkout', methods=['POST'])
def mock_checkout_route():
    data = request.json
    cart_items = data.get('cartItems', [])
    if not cart_items: return jsonify({"error": "Cart is empty"}), 400
    total_price = sum(float(item.get('price', '$0').replace('$', '')) for item in cart_items if item.get('price'))
    summary_items_str = "\n- ".join([f"{item.get('name', 'Unknown')} ({item.get('price', '$0')})" for item in cart_items])
    summary_message = f"Checkout for {len(cart_items)} items. Total: ${total_price:.2f}.\nItems:\n- {summary_items_str}"
    app.logger.info(f"Mock Checkout: {summary_message}")
    return jsonify({"message": summary_message, "totalItems": len(cart_items), "totalPrice": f"${total_price:.2f}"})

if __name__ == '__main__':
    # use_reloader=False is important if model loading on startup is heavy
    # and you don't want it to happen twice during Flask's debug auto-reload.
    app.run(debug=True, use_reloader=False) 