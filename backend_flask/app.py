# backend_flask/app.py
import os
import uuid
import json
from flask import Flask, request, jsonify, render_template, url_for, current_app
from werkzeug.utils import secure_filename # Ensure this is imported
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from dotenv import load_dotenv
load_dotenv()

# AI Core Modules - These should be importable after Python path setup
from ai_core.vision_models import load_vit_model, extract_vit_features, get_image_description_openai
from ai_core.language_models import load_spacy_model, extract_keywords_spacy, get_refined_search_gemini

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
UPLOAD_FOLDER = 'uploads' # Relative to app.root_path if not absolute
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # DEFINED GLOBALLY HERE

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['PRODUCT_IMAGE_FOLDER'] = os.path.join('static', 'product_images') # Relative to app.root_path

# Ensure necessary folders exist (relative to where app.py is run from, or use app.root_path for safety)
# When app starts, app.root_path is the directory containing app.py
# So, os.path.join(app.root_path, UPLOAD_FOLDER) is more robust if UPLOAD_FOLDER is just 'uploads'
# However, Flask's app.config['UPLOAD_FOLDER'] usually handles this. Let's ensure they are created based on app.root_path
# for clarity if they don't exist.
# This creation logic is better placed *after* app object is created if using app.root_path.

# --- Helper Function (needs ALLOWED_EXTENSIONS) ---
def allowed_file(filename):
    """Checks if the filename has an allowed extension."""
    if not filename or '.' not in filename:
        return False
    ext_parts = filename.rsplit('.', 1)
    if len(ext_parts) < 2: # No extension found
        return False
    return ext_parts[1].lower() in ALLOWED_EXTENSIONS # Accesses global ALLOWED_EXTENSIONS


# --- Initialize AI Clients and Models, Create Folders within App Context ---
with app.app_context():
    # Ensure upload and product image folders exist relative to the app's root path
    upload_folder_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    product_image_folder_path = os.path.join(current_app.root_path, current_app.config['PRODUCT_IMAGE_FOLDER'])
    os.makedirs(upload_folder_path, exist_ok=True)
    os.makedirs(product_image_folder_path, exist_ok=True)
    current_app.logger.info(f"Upload folder ensured at: {upload_folder_path}")
    current_app.logger.info(f"Product image folder ensured at: {product_image_folder_path}")


    # OpenAI Client
    if not OPENAI_API_KEY:
        current_app.logger.warning("OPENAI_API_KEY not found. OpenAI features will be disabled.")
        openai_client = None # Explicitly set to None
    else:
        try:
            openai_client = openai_sdk.OpenAI(api_key=OPENAI_API_KEY)
            current_app.logger.info("OpenAI client initialized successfully.")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize OpenAI client: {e}")
            openai_client = None

    # Google Generative AI Configuration
    if not GOOGLE_API_KEY:
        current_app.logger.warning("GOOGLE_API_KEY not found. Gemini features will be disabled.")
    else:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            current_app.logger.info("Google Generative AI configured successfully.")
        except Exception as e:
            current_app.logger.error(f"Failed to configure Google Generative AI: {e}")

    # Load ViT and spaCy models (their internal logic handles loading once)
    load_vit_model() # from ai_core.vision_models
    load_spacy_model() # from ai_core.language_models


# --- Product Database (Update 'image_path_for_ai' with LOCAL paths relative to app.root_path) ---
MOCK_PRODUCTS_DB = [
    {"id": "prod1", "name": "Classic Red Cotton T-Shirt", "price": "$19.99", "type": "T-Shirt", "category": "Apparel", "style": "Casual", "material": "Cotton", "color_tags": ["red", "solid"], "description": "A comfortable and stylish red t-shirt made from 100% cotton. Perfect for everyday wear.", "images": [f"https://via.placeholder.com/400x450/FF6347/FFFFFF?Text=RedTee1", f"https://via.placeholder.com/400x450/CD5C5C/FFFFFF?Text=RedTee2"], "image_path_for_ai": "static/product_images/red_tshirt.jpg", "sizes": ["S", "M", "L"], "colors": ["Red", "Dark Red"], "detailedReasons": ["Matches color 'Red'"], "embedding": None},
    {"id": "prod2", "name": "Blue Slim-Fit Denim Jeans", "price": "$49.99", "type": "Jeans", "category": "Apparel", "style": "Casual", "material": "Denim", "color_tags": ["blue", "denim"], "description": "Perfectly fitting blue slim-fit denim jeans. A wardrobe staple.", "images": [f"https://via.placeholder.com/400x450/1E90FF/FFFFFF?Text=BlueJeans1"], "image_path_for_ai": "static/product_images/blue_jeans.jpg", "sizes": ["28", "30", "32"], "colors": ["Blue"], "detailedReasons": ["Pairs with T-Shirts"], "embedding": None},
    {"id": "prod3", "name": "Stylish Grey Running Sneakers", "price": "$79.00", "type": "Sneakers", "category": "Footwear", "style": "Sporty", "material": "Mesh", "color_tags": ["grey", "black", "athletic"], "description": "Comfortable and trendy grey running sneakers with breathable mesh. Ideal for workouts or casual outings.", "images": [f"https://via.placeholder.com/400x450/D3D3D3/000000?Text=Sneakers1", f"https://via.placeholder.com/400x450/A9A9A9/FFFFFF?Text=Sneakers2"], "image_path_for_ai": "static/product_images/grey_sneakers.jpg", "sizes": ["8", "9", "10"], "colors": ["Grey", "Black"], "detailedReasons": ["Good for athletic wear"], "embedding": None},
    # Add other products here, ensuring 'image_path_for_ai' is correct
    {"id": "prod4", "name": "Summer Floral Maxi Dress", "price": "$65.00", "type": "Dress", "category": "Apparel", "style": "Bohemian", "material": "Rayon", "color_tags": ["pink", "floral", "multi-color", "summer"], "description": "Light and airy floral maxi dress for summer, bohemian style. Features a vibrant floral print.", "images": [f"https://via.placeholder.com/400x450/FFC0CB/000000?Text=FloralDress1"], "image_path_for_ai": "static/product_images/floral_dress.jpg", "sizes": ["S", "M", "L"], "colors": ["Pink Floral"], "detailedReasons": ["Vibe: Summer", "Pattern: Floral"], "embedding": None},
    {"id": "prod5", "name": "Classic Brown Leather Belt", "price": "$25.00", "type": "Belt", "category": "Accessory", "style": "Classic", "material": "Leather", "color_tags": ["brown", "leather"], "description": "Classic brown genuine leather belt with a timeless buckle. Adds a polished touch to any outfit.", "images": [f"https://via.placeholder.com/400x450/8B4513/FFFFFF?Text=Belt1"], "image_path_for_ai": "static/product_images/leather_belt.jpg", "sizes": ["One Size"], "colors": ["Brown"], "detailedReasons": ["Accessory for Jeans"], "embedding": None},
    {"id": "prod6", "name": "Comfy Light Blue Hoodie", "price": "$55.99", "type": "Hoodie", "category": "Apparel", "style": "Casual", "material": "Fleece", "color_tags": ["blue", "light blue", "cozy"], "description": "A very comfortable light blue hoodie made of soft fleece. Features a kangaroo pocket and drawstring hood.", "images": [f"https://via.placeholder.com/400x450/B0C4DE/000000?Text=Hoodie1"], "image_path_for_ai": "static/product_images/blue_hoodie.jpg", "sizes": ["M", "L", "XL"], "colors": ["Light Blue"], "detailedReasons": ["Great for cool evenings"], "embedding": None}
]
AI_PRODUCT_DATABASE = [] # Will be populated by preprocess_product_database


def preprocess_product_database():
    global AI_PRODUCT_DATABASE
    AI_PRODUCT_DATABASE = [] # Reset
    
    # Access current_app here, as this function is called within app_context
    _, vit_model_loaded = load_vit_model() # from ai_core.vision_models
    if not vit_model_loaded:
        current_app.logger.error("ViT model not loaded during preprocess. Cannot generate ViT embeddings.")
        # Populate AI_PRODUCT_DATABASE without embeddings for text search capabilities
        for product_template in MOCK_PRODUCTS_DB:
            product = product_template.copy()
            product["embedding"] = None
            product["imageUrl"] = product.get("images")[0] if product.get("images") else "https://via.placeholder.com/260x250/CCCCCC/000000?Text=NoImg"
            AI_PRODUCT_DATABASE.append(product)
        return

    current_app.logger.info("Preprocessing product database for ViT features...")
    processed_count = 0
    for product_template in MOCK_PRODUCTS_DB:
        product = product_template.copy()
        rel_image_path = product.get('image_path_for_ai')
        image_to_process_path = None
        if rel_image_path:
            # Construct absolute path using app.root_path
            image_to_process_path = os.path.join(current_app.root_path, rel_image_path)
            # current_app.logger.debug(f"DEBUG PREPROCESS: Checking path: {image_to_process_path} for product {product['name']}")

        if image_to_process_path and os.path.exists(image_to_process_path):
            embedding = extract_vit_features(image_to_process_path) # from ai_core.vision_models
            if embedding is not None:
                product["embedding"] = embedding
                processed_count += 1
            else:
                product["embedding"] = None
                current_app.logger.warning(f"Failed to get ViT embedding for {product['name']} (path: {image_to_process_path})")
        else:
            product["embedding"] = None
            current_app.logger.warning(f"Product '{product['name']}' missing valid local 'image_path_for_ai': {image_to_process_path}. Skipping ViT embedding.")
        
        product["imageUrl"] = product.get("images")[0] if product.get("images") else "https://via.placeholder.com/260x250/CCCCCC/000000?Text=NoImg"
        AI_PRODUCT_DATABASE.append(product)
    current_app.logger.info(f"Finished ViT preprocessing. {processed_count}/{len(MOCK_PRODUCTS_DB)} products have ViT embeddings.")


# Call preprocessing within app context after app object is created and configured
with app.app_context():
    preprocess_product_database()


# backend_flask/app.py

# ... (other parts of app.py) ...

def generate_final_recommendations(query_image_path=None, text_prompt="", top_k=10):
    # Initialize variables at the top of the function scope
    openai_description = "N/A (OpenAI not used or no image provided)"
    gemini_refinement_data = {"error": "Gemini not used or no relevant input."} # Default error/NA state
    visual_recommendations = []
    
    # 1. Get OpenAI Vision description and ViT features if an image is provided
    if query_image_path:
        # Pass the globally initialized openai_client (if available)
        if openai_client:
            openai_description = get_image_description_openai(query_image_path, openai_client)
        else:
            current_app.logger.warning("OpenAI client not available for image description in generate_final_recommendations.")
            openai_description = "OpenAI client not available."
        
        query_embedding = extract_vit_features(query_image_path)
        if query_embedding is not None and AI_PRODUCT_DATABASE:
            db_embeddings_tuples = [(p["embedding"], p) for p in AI_PRODUCT_DATABASE if p.get("embedding") is not None]
            if db_embeddings_tuples:
                db_embeddings = np.array([t[0] for t in db_embeddings_tuples])
                products_with_embeddings = [t[1] for t in db_embeddings_tuples]
                
                similarities = cosine_similarity(query_embedding.reshape(1, -1), db_embeddings)[0]
                sorted_indices = np.argsort(similarities)[::-1]

                for i in sorted_indices:
                    if len(visual_recommendations) < top_k * 2: # Get more visual matches initially
                        product = products_with_embeddings[i].copy()
                        similarity_score = float(similarities[i])
                        product["recommendationReason"] = f"Visually similar (ViT Score: {similarity_score:.2f})"
                        product["detailedReasons"] = [f"ViT Similarity: {similarity_score:.2f}"]
                        product["visual_score"] = similarity_score
                        visual_recommendations.append(product)
            else:
                current_app.logger.warning("No product ViT embeddings in AI_PRODUCT_DATABASE for visual comparison.")
        elif not AI_PRODUCT_DATABASE:
             current_app.logger.warning("AI_PRODUCT_DATABASE is empty, cannot perform visual search.")
        else: # query_embedding is None
             current_app.logger.warning(f"Could not get ViT embedding for query image: {query_image_path}")
    
    # 2. spaCy keyword extraction from text_prompt
    spacy_keywords = extract_keywords_spacy(text_prompt) if text_prompt else []

    # 3. Gemini for refinement
    # Use the potentially updated openai_description
    current_desc_for_gemini = openai_description if "Error" not in openai_description and "N/A" not in openai_description and "not available" not in openai_description.lower() else "No specific visual input provided."
    product_ctx_str = "Initial visual ideas: " + ", ".join([p['name'] for p in visual_recommendations[:3]]) if visual_recommendations else ""
    
    # Only call Gemini if there's substantial input to work with
    if text_prompt or current_desc_for_gemini != "No specific visual input provided.":
        gemini_refinement_data = get_refined_search_gemini(current_desc_for_gemini, text_prompt, product_ctx_str)
    else:
        # If no text prompt and no valid image description, Gemini might not be useful
        gemini_refinement_data = {"message": "Insufficient input for Gemini refinement."}


    # 4. Combine visual similarity, text prompt, spaCy keywords, and Gemini insights
    candidate_products = visual_recommendations if visual_recommendations else [p.copy() for p in AI_PRODUCT_DATABASE]
    if not candidate_products:
        current_app.logger.info("No candidate products available for recommendation.")
        # Return the initialized openai_description and gemini_refinement_data
        return [], openai_description, gemini_refinement_data

    # ... (rest of the scoring and sorting logic from your previous full app.py for generate_final_recommendations) ...
    # This part should be identical to the one I provided in the "fully revised app.py" before this error.
    # I'll paste it again for completeness of this function:
    scored_recommendations = []
    all_search_keywords = set(text_prompt.lower().split())
    all_search_keywords.update(spacy_keywords)

    if isinstance(gemini_refinement_data, dict) and not gemini_refinement_data.get("error"):
        gemini_key_attrs = gemini_refinement_data.get("key_attributes", [])
        gemini_refined_query = gemini_refinement_data.get("refined_search_query", "")
        if isinstance(gemini_key_attrs, list): all_search_keywords.update([attr.lower() for attr in gemini_key_attrs])
        if isinstance(gemini_refined_query, str): all_search_keywords.update(gemini_refined_query.lower().split())
    all_search_keywords = list(filter(None, all_search_keywords)) 

    for product in candidate_products:
        score = product.get("visual_score", 0.0) * 10.0
        current_reasons = product.get("detailedReasons", [])
        
        text_match_count = 0
        product_text_corpus = (f"{product.get('name','')} {product.get('description','')} {product.get('type','')} "
                               f"{product.get('category','')} {product.get('style','')} {product.get('material','')} "
                               f"{' '.join(product.get('color_tags',[]))}").lower()
        
        matched_kw_for_this_product = [kw for kw in all_search_keywords if kw and kw in product_text_corpus] # Ensure kw is not empty
        text_match_count = len(set(matched_kw_for_this_product))
        
        score += text_match_count * 2.5

        if text_match_count > 0:
            reason_str = f"Matches keywords: {', '.join(list(set(matched_kw_for_this_product)))}"
            current_reasons.append(reason_str)
            current_rec_reason = product.get("recommendationReason", "")
            if "Visually similar" in current_rec_reason:
                 product["recommendationReason"] = f"{current_rec_reason} & {reason_str.lower()}"
            elif not current_rec_reason or current_rec_reason.startswith("N/A"): # If no reason yet, or default N/A
                 product["recommendationReason"] = reason_str
            else: 
                 product["recommendationReason"] = f"{current_rec_reason}, also {reason_str.lower()}"
        
        product["final_score"] = score
        product["detailedReasons"] = list(set(current_reasons))
        scored_recommendations.append(product)

    scored_recommendations.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    final_recommendations = scored_recommendations[:top_k]
    
    if not final_recommendations and AI_PRODUCT_DATABASE:
        final_recommendations = [p.copy() for i, p in enumerate(AI_PRODUCT_DATABASE) if i < top_k]
        for rec in final_recommendations: 
            rec["recommendationReason"] = "Popular item (fallback)"
            rec["final_score"] = 0.1 # Give fallback a minimal score if needed for display consistency
            
    for rec in final_recommendations:
        rec["imageUrl"] = rec.get("images")[0] if rec.get("images") else (rec.get("imageUrl") or "https://via.placeholder.com/260x250/CCCCCC/000000?Text=NoImg")
        base_reason = rec.get("recommendationReason", "Recommended")
        final_score_val = rec.get('final_score', 0.0)
        
        if final_score_val > 0.01 or "fallback" not in base_reason.lower() : # Only add score if meaningful or not fallback
            rec["recommendationReason"] = f"{base_reason} (Score: {final_score_val:.1f})"
        else: # If score is 0 and not fallback (e.g. no matches), or it is fallback.
            if "fallback" in base_reason.lower():
                rec["recommendationReason"] = base_reason # Just "Popular item (fallback)"
            elif not base_reason or base_reason == "Recommended": # If no specific reason from matching
                 rec["recommendationReason"] = "Considered (low relevance)"


        if "visual_score" in rec: del rec["visual_score"] # Clean up intermediate score

    return final_recommendations, openai_description, gemini_refinement_data

# ... (rest of your app.py: routes, etc.)
# --- Routes ---
@app.route('/')
def index():
    initial_recs, _, _ = generate_final_recommendations(text_prompt="trending fashion and home decor", top_k=8)
    return render_template('index.html', initial_recommendations=json.dumps(initial_recs))

@app.route('/upload_image', methods=['POST'])
def upload_image_route():
    if 'imageFile' not in request.files: return jsonify({"error": "No image file part"}), 400
    file = request.files['imageFile']
    if not file.filename: return jsonify({"error": "No selected file"}), 400 # Check for empty filename

    # Use the globally defined ALLOWED_EXTENSIONS
    if file and allowed_file(file.filename): # allowed_file function now uses global ALLOWED_EXTENSIONS
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        # Use app.config for upload folder path consistency
        filepath = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            prompt_text = request.form.get('prompt', '')
            
            recommendations, openai_desc, gemini_refine = generate_final_recommendations(
                query_image_path=filepath, text_prompt=prompt_text
            )
            
            # URL for frontend to display the image it just uploaded
            # The UPLOAD_FOLDER is directly under app.root_path, not necessarily under 'static' for direct access via url_for('static',...)
            # So, we serve it from a different route or make 'uploads' a static folder.
            # For simplicity with url_for, if UPLOAD_FOLDER is 'uploads' at root of backend_flask:
            # image_url_for_preview = url_for('static', filename=f"../{current_app.config['UPLOAD_FOLDER']}/{filename}") # Path relative to static
            # A better way is to serve uploads from a dedicated route or configure 'uploads' as static.
            # Let's assume 'uploads' is served. If not, this URL might need adjustment or a new route.
            # If UPLOAD_FOLDER is at the same level as 'static', this relative path is tricky.
            # Simplest for now: ensure UPLOAD_FOLDER is accessible.
            # If UPLOAD_FOLDER is inside static: url_for('static', filename=f"{UPLOAD_FOLDER_NAME_INSIDE_STATIC}/{filename}")
            # If UPLOAD_FOLDER is at root: current_app.config['UPLOAD_FOLDER'] + '/' + filename and serve it.
            # For this example, let's assume UPLOAD_FOLDER is served directly if configured as such by Flask.
            # A common pattern is to have an endpoint that serves these files.
            # For now, the previous relative pathing for url_for might work if UPLOAD_FOLDER is configured as static or via a route.
            # Let's ensure the path is correct for preview, assuming UPLOAD_FOLDER is a sibling to 'static' under app.root_path
            image_url_for_preview = f"/{current_app.config['UPLOAD_FOLDER']}/{filename}" # Direct path if 'uploads' is served
            # This requires 'uploads' to be served, e.g. if app.static_folder is reconfigured or a specific route is made.
            # For this hackathon, let's try a simpler approach if 'uploads' is directly under backend_flask
            # and Flask's default static handling might not pick it up.
            # The image_preview_url in main.js uses the response from here.
            # The provided URL should be accessible by the browser.

            # If 'uploads' is not served directly, the preview URL from client-side FileReader is more reliable.
            # The server returns the path mainly for its own reference if needed later or for confirmation.
            # The client-side preview in main.js (using FileReader) is independent of this server URL for display.
            # The `image_preview_url` here is more of a confirmation or if client wants to re-fetch.

            # For the hackathon, we are NOT deleting filepath immediately to allow potential direct access if 'uploads' is made static.
            # Or, the client-side preview is what the user sees.

            return jsonify({
                "message": "Image processed",
                "filename_server_temp": filename, # Name of file in server's UPLOAD_FOLDER
                "image_preview_url": image_url_for_preview, # Path browser might try to hit
                "recommendations": recommendations,
                "openai_description": openai_desc,
                "gemini_refinement": gemini_refine
            })
        except Exception as e:
            current_app.logger.error(f"Error processing uploaded image route: {e}", exc_info=True)
            if 'filepath' in locals() and os.path.exists(filepath):
                try: os.remove(filepath)
                except: current_app.logger.error(f"Failed to remove {filepath} on error.")
            return jsonify({"error": f"Server error processing image: {str(e)}"}), 500
    else:
        current_ext = "unknown"
        if file and file.filename and '.' in file.filename:
            current_ext = file.filename.rsplit('.', 1)[1].lower()
        current_app.logger.warning(f"File type not allowed: {file.filename if file else 'No file'} (extension: {current_ext})")
        return jsonify({"error": f"File type '{current_ext}' not allowed. Please upload one of: {', '.join(ALLOWED_EXTENSIONS)}."}), 400


@app.route('/get_recommendations', methods=['POST'])
def get_recommendations_route():
    data = request.json
    prompt_text = data.get('prompt', '')
    try:
        recommendations, _, gemini_refine = generate_final_recommendations(text_prompt=prompt_text)
        return jsonify({
            "recommendations": recommendations,
            "gemini_refinement": gemini_refine 
        })
    except Exception as e:
        current_app.logger.error(f"Error getting text recommendations: {e}", exc_info=True)
        return jsonify({"error": "Failed to get recommendations"}), 500

@app.route(f'/{UPLOAD_FOLDER}/<filename>')
def send_uploaded_file(filename):
    # Route to serve uploaded files for preview if needed.
    # Ensure UPLOAD_FOLDER is correctly joined with app.root_path
    upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_dir, filename)


@app.route('/mock_checkout', methods=['POST'])
def mock_checkout_route():
    data = request.json
    cart_items = data.get('cartItems', [])
    if not cart_items: return jsonify({"error": "Cart is empty"}), 400
    
    total_price = 0
    for item in cart_items:
        try:
            # Ensure price is a string before trying to replace '$'
            price_str = str(item.get('price', '0'))
            price_val = float(price_str.replace('$', ''))
            total_price += price_val
        except ValueError:
            current_app.logger.warning(f"Could not parse price for item: {item.get('name')}. Price was: {item.get('price')}")
            # Decide how to handle unparseable prices, e.g., skip or default to 0

    summary_items_str = "\n- ".join([f"{item.get('name', 'Unknown')} ({item.get('price', '$0')})" for item in cart_items])
    summary_message = f"Checkout for {len(cart_items)} items. Total: ${total_price:.2f}.\nItems:\n- {summary_items_str}"
    current_app.logger.info(f"Mock Checkout: {summary_message}")
    return jsonify({"message": summary_message, "totalItems": len(cart_items), "totalPrice": f"${total_price:.2f}"})

if __name__ == '__main__':
    # For send_from_directory to work easily, UPLOAD_FOLDER needs to be known to Flask's static system
    # or served via a route. Adding the route above is one way.
    # If using `send_from_directory`, import it:
    from flask import send_from_directory # Add this import at the top
    app.run(debug=True, use_reloader=False)