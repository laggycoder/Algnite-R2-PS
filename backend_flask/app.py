import os
import uuid
import json
from flask import Flask, request, jsonify, render_template, url_for, current_app, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image # Keep for potential direct use if needed, though ViT processing uses it internally
from sklearn.metrics.pairwise import cosine_similarity # Keep for ViT
import numpy as np # Keep for ViT

from dotenv import load_dotenv
load_dotenv() # Load .env file from the current directory (backend_flask)

# AI Core Modules
from ai_core.vision_models import load_vit_model, extract_vit_features, get_image_description_openai
from ai_core.language_models import load_spacy_model, extract_keywords_spacy, get_refined_search_gemini
from ai_core.product_catalog import load_and_preprocess_catalog, get_catalog_products # Key import

# OpenAI SDK
import openai as openai_sdk
openai_client = None # Will be initialized in app_context
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google Generative AI
import google.generativeai as genai
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# --- Flask App Initialization ---
app = Flask(__name__)

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# --- Helper Function ---
def allowed_file(filename):
    """Checks if the filename has an allowed extension."""
    if not filename or '.' not in filename: return False
    ext_parts = filename.rsplit('.', 1)
    if len(ext_parts) < 2: return False
    return ext_parts[1].lower() in ALLOWED_EXTENSIONS


# --- Initialize AI Clients, Models, and Product Catalog within App Context ---
with app.app_context():
    upload_folder_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_folder_path, exist_ok=True)
    current_app.logger.info(f"Upload folder ensured at: {upload_folder_path}")

    if not OPENAI_API_KEY:
        current_app.logger.warning("OPENAI_API_KEY not found. OpenAI features will be disabled.")
    else:
        try:
            openai_client = openai_sdk.OpenAI(api_key=OPENAI_API_KEY)
            current_app.logger.info("OpenAI client initialized successfully.")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize OpenAI client: {e}")
            openai_client = None

    if not GOOGLE_API_KEY:
        current_app.logger.warning("GOOGLE_API_KEY not found. Gemini features will be disabled.")
    else:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            current_app.logger.info("Google Generative AI configured successfully.")
        except Exception as e:
            current_app.logger.error(f"Failed to configure Google Generative AI: {e}")

    load_vit_model()
    load_spacy_model()
    load_and_preprocess_catalog()


# --- Core Recommendation Logic ---
def generate_final_recommendations(query_image_path=None, text_prompt="", top_k=10):
    current_catalog_with_embeddings = get_catalog_products()
    
    if not current_catalog_with_embeddings:
        current_app.logger.error("Product catalog is empty or not loaded! Cannot generate recommendations.")
        return [], "Error: Product catalog is critically empty or failed to load.", {"error": "Product catalog unavailable."}

    openai_description = "N/A (OpenAI not used or no image provided)"
    gemini_refinement_data = {"error": "Gemini not used or input insufficient."}
    visual_recommendations = []
    
    if query_image_path:
        if openai_client:
            openai_description = get_image_description_openai(query_image_path, openai_client)
        else:
            current_app.logger.warning("OpenAI client not available for image description.")
            openai_description = "OpenAI client not available."
        
        query_embedding = extract_vit_features(query_image_path)
        if query_embedding is not None:
            db_embeddings_tuples = [(p["embedding"], p) for p in current_catalog_with_embeddings if p.get("embedding") is not None]
            if db_embeddings_tuples:
                db_embeddings = np.array([t[0] for t in db_embeddings_tuples])
                products_with_embeddings = [t[1] for t in db_embeddings_tuples]
                
                similarities = cosine_similarity(query_embedding.reshape(1, -1), db_embeddings)[0]
                sorted_indices = np.argsort(similarities)[::-1]

                for i in sorted_indices:
                    if len(visual_recommendations) < top_k * 2: # Get more for potential filtering
                        product = products_with_embeddings[i].copy()
                        similarity_score = float(similarities[i])
                        product["recommendationReason"] = f"Visually similar (ViT Score: {similarity_score:.2f})"
                        product["detailedReasons"] = [f"ViT Similarity: {similarity_score:.2f}"]
                        product["visual_score"] = similarity_score
                        visual_recommendations.append(product)
            else:
                current_app.logger.warning("No ViT embeddings found in the product catalog for visual comparison.")
        else:
             current_app.logger.warning(f"Could not get ViT embedding for query image: {query_image_path}")
    
    spacy_keywords = extract_keywords_spacy(text_prompt) if text_prompt else []

    current_desc_for_gemini = openai_description if "Error" not in openai_description and "N/A" not in openai_description and "not available" not in openai_description.lower() else "No specific visual input provided."
    product_ctx_str = "Initial visual ideas: " + ", ".join([p['name'] for p in visual_recommendations[:3]]) if visual_recommendations else ""
    
    if text_prompt or current_desc_for_gemini != "No specific visual input provided.":
        gemini_refinement_data = get_refined_search_gemini(current_desc_for_gemini, text_prompt, product_ctx_str)
    else:
        gemini_refinement_data = {"message": "Insufficient input for Gemini refinement."}

    candidate_products = visual_recommendations if visual_recommendations else [p.copy() for p in current_catalog_with_embeddings]
    if not candidate_products:
        current_app.logger.info("No candidate products for recommendation.")
        return [], openai_description, gemini_refinement_data

    scored_recommendations = []
    all_search_keywords = set(text_prompt.lower().split())
    all_search_keywords.update(spacy_keywords)

    if isinstance(gemini_refinement_data, dict) and not gemini_refinement_data.get("error"):
        gemini_key_attrs = gemini_refinement_data.get("key_attributes", [])
        gemini_refined_query_terms = gemini_refinement_data.get("refined_search_query", "").lower().split() # Changed key name
        if isinstance(gemini_key_attrs, list): all_search_keywords.update([attr.lower() for attr in gemini_key_attrs])
        all_search_keywords.update(gemini_refined_query_terms)
    all_search_keywords = list(filter(None, all_search_keywords)) 

    for product in candidate_products:
        product_copy = product.copy() # Work with a copy to avoid modifying original catalog items in memory
        score = product_copy.get("visual_score", 0.0) * 10.0
        current_reasons = product_copy.get("detailedReasons", [])[:] # Copy list

        text_match_count = 0
        product_text_corpus = (f"{product_copy.get('name','')} {product_copy.get('description','')} {product_copy.get('type','')} "
                               f"{product_copy.get('category','')} {product_copy.get('style','')} {product_copy.get('material','')} "
                               f"{' '.join(product_copy.get('color_tags',[]))}").lower()
        
        matched_kw_for_this_product = [kw for kw in all_search_keywords if kw and kw in product_text_corpus]
        text_match_count = len(set(matched_kw_for_this_product))
        score += text_match_count * 2.5

        if text_match_count > 0:
            reason_str = f"Matches keywords: {', '.join(list(set(matched_kw_for_this_product)))}"
            current_reasons.append(reason_str)
            current_rec_reason = product_copy.get("recommendationReason", "")
            if "Visually similar" in current_rec_reason: product_copy["recommendationReason"] = f"{current_rec_reason} & {reason_str.lower()}"
            elif not current_rec_reason or current_rec_reason.startswith("N/A"): product_copy["recommendationReason"] = reason_str
            else: product_copy["recommendationReason"] = f"{current_rec_reason}, also {reason_str.lower()}"
        
        product_copy["final_score"] = score
        product_copy["detailedReasons"] = list(set(current_reasons))
        scored_recommendations.append(product_copy)

    scored_recommendations.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    final_recommendations_raw = scored_recommendations[:top_k]
    
    if not final_recommendations_raw and current_catalog_with_embeddings:
        final_recommendations_raw = [p.copy() for i, p in enumerate(current_catalog_with_embeddings) if i < top_k]
        for rec in final_recommendations_raw: 
            rec["recommendationReason"] = "Popular item (fallback)"
            rec["final_score"] = 0.1 
    
    # Prepare for JSON: remove ndarray embeddings and visual_score from the final list
    final_recommendations_for_json = []
    for rec_raw in final_recommendations_raw:
        rec_json_safe = rec_raw.copy()
        rec_json_safe["imageUrl"] = rec_json_safe.get("images")[0] if rec_json_safe.get("images") else (rec_json_safe.get("imageUrl") or "https://via.placeholder.com/260x250/CCCCCC/000000?Text=NoImg")
        base_reason = rec_json_safe.get("recommendationReason", "Recommended")
        final_score_val = rec_json_safe.get('final_score', 0.0)
        
        if final_score_val > 0.01 or "fallback" not in base_reason.lower() :
            rec_json_safe["recommendationReason"] = f"{base_reason} (Score: {final_score_val:.1f})"
        elif "fallback" in base_reason.lower(): rec_json_safe["recommendationReason"] = base_reason
        elif not base_reason or base_reason == "Recommended": rec_json_safe["recommendationReason"] = "Considered (low relevance)"
        
        if "embedding" in rec_json_safe: del rec_json_safe["embedding"]
        if "visual_score" in rec_json_safe: del rec_json_safe["visual_score"] # Already used for final_score
        
        final_recommendations_for_json.append(rec_json_safe)

    return final_recommendations_for_json, openai_description, gemini_refinement_data

# --- Routes ---
@app.route('/')
def index():
    initial_recs_for_json, _, _ = generate_final_recommendations(
        text_prompt="trending fashion and popular apparel", top_k=8
    )
    # No need to further process initial_recs_for_json, it's already prepared by generate_final_recommendations
    return render_template('index.html', initial_recommendations=json.dumps(initial_recs_for_json))

@app.route('/upload_image', methods=['POST'])
def upload_image_route():
    if 'imageFile' not in request.files: return jsonify({"error": "No image file part"}), 400
    file = request.files['imageFile']
    if not file.filename: return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            prompt_text = request.form.get('prompt', '')
            
            recommendations_json_safe, openai_desc, gemini_refine = generate_final_recommendations(
                query_image_path=filepath, text_prompt=prompt_text
            )
            
            image_url_for_preview = url_for('send_uploaded_file', filename=filename)
            
            return jsonify({
                "message": "Image processed",
                "filename_server_temp": filename,
                "image_preview_url": image_url_for_preview,
                "recommendations": recommendations_json_safe, # Already JSON safe
                "openai_description": openai_desc,
                "gemini_refinement": gemini_refine
            })
        except Exception as e:
            current_app.logger.error(f"Error processing uploaded image route: {e}", exc_info=True)
            if 'filepath' in locals() and os.path.exists(filepath):
                try: os.remove(filepath)
                except Exception as e_rem: current_app.logger.error(f"Failed to remove temp file {filepath} on error: {e_rem}")
            return jsonify({"error": f"Server error processing image: {str(e)}"}), 500
    else:
        current_ext = "unknown"
        if file and file.filename and '.' in file.filename:
            current_ext = file.filename.rsplit('.', 1)[1].lower()
        current_app.logger.warning(f"File type not allowed: {file.filename if file else 'No file'} (extension: {current_ext})")
        return jsonify({"error": f"File type '{current_ext}' not allowed. Please upload one of: {', '.join(ALLOWED_EXTENSIONS)}."}), 400

@app.route(f'/{UPLOAD_FOLDER}/<path:filename>')
def send_uploaded_file(filename):
    upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_dir, filename)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations_route():
    data = request.json
    prompt_text = data.get('prompt', '')
    try:
        recommendations_json_safe, _, gemini_refine = generate_final_recommendations(text_prompt=prompt_text)
        return jsonify({
            "recommendations": recommendations_json_safe, # Already JSON safe
            "gemini_refinement": gemini_refine 
        })
    except Exception as e:
        current_app.logger.error(f"Error getting text recommendations: {e}", exc_info=True)
        return jsonify({"error": "Failed to get recommendations"}), 500

@app.route('/mock_checkout', methods=['POST'])
def mock_checkout_route():
    data = request.json
    cart_items = data.get('cartItems', [])
    if not cart_items: return jsonify({"error": "Cart is empty"}), 400
    total_price = 0
    for item in cart_items:
        try:
            price_str = str(item.get('price', '0'))
            price_val = float(price_str.replace('$', ''))
            total_price += price_val
        except ValueError:
            current_app.logger.warning(f"Could not parse price for item: {item.get('name')}. Price was: {item.get('price')}")
    summary_items_str = "\n- ".join([f"{item.get('name', 'Unknown')} ({item.get('price', '$0')})" for item in cart_items])
    summary_message = f"Checkout for {len(cart_items)} items. Total: ${total_price:.2f}.\nItems:\n- {summary_items_str}"
    current_app.logger.info(f"Mock Checkout: {summary_message}")
    return jsonify({"message": summary_message, "totalItems": len(cart_items), "totalPrice": f"${total_price:.2f}"})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)