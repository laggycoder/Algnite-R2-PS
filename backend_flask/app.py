import os
import uuid
import json
from datetime import datetime # For order timestamps
from flask import (
    Flask, request, jsonify, render_template, url_for, 
    current_app, send_from_directory, flash, redirect, session
)
from werkzeug.utils import secure_filename
# from werkzeug.security import generate_password_hash, check_password_hash # Using bcrypt

from dotenv import load_dotenv
load_dotenv()

# Flask extensions
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Custom Modules
from . import db  # For SQLite connection
from .models import User # Your User model for SQLite
from .ai_core.vision_models import load_vit_model, extract_vit_features, get_image_description_openai
from .ai_core.language_models import load_spacy_model, extract_keywords_spacy, get_refined_search_gemini
from .ai_core.product_catalog import load_and_preprocess_catalog, get_catalog_products

# OpenAI SDK
import openai as openai_sdk
openai_client = None 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google Generative AI
import google.generativeai as genai
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# SQLite specific imports
import sqlite3 
import numpy as np # Keep for ViT
from sklearn.metrics.pairwise import cosine_similarity # Keep for ViT
# from PIL import Image # Already imported in vision_models.py if needed there directly

# --- Flask App Initialization & Configuration ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads' # Relative to app.root_path
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_change_this_123!')
# ALLOWED_EXTENSIONS for file uploads
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_api_route' 
login_manager.login_message_category = "info"

db.init_app(app) # Initialize SQLite database

# --- User Loader for Flask-Login ---
@login_manager.user_loader
def load_user(user_id_str):
    return User.get_by_id(user_id_str)

# --- Initialize AI Clients, Models, and Product Catalog ---
with app.app_context():
    upload_folder_path = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_folder_path, exist_ok=True)
    current_app.logger.info(f"Upload folder ensured at: {upload_folder_path}")

    if not OPENAI_API_KEY: current_app.logger.warning("OPENAI_API_KEY missing.")
    else:
        try: openai_client = openai_sdk.OpenAI(api_key=OPENAI_API_KEY); current_app.logger.info("OpenAI client OK.")
        except Exception as e: current_app.logger.error(f"OpenAI client init error: {e}"); openai_client = None
    
    if not GOOGLE_API_KEY: current_app.logger.warning("GOOGLE_API_KEY missing.")
    else:
        try: genai.configure(api_key=GOOGLE_API_KEY); current_app.logger.info("Gemini configured OK.")
        except Exception as e: current_app.logger.error(f"Gemini config error: {e}")

    load_vit_model()
    load_spacy_model()
    load_and_preprocess_catalog()

# --- Helper Function ---
def allowed_file(filename):
    if not filename or '.' not in filename: return False
    # Use app.config to get ALLOWED_EXTENSIONS
    return filename.rsplit('.', 1)[1].lower() in app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})


# --- Core Recommendation Logic (Incorporating User Preferences) ---
def generate_final_recommendations(query_image_path=None, text_prompt="", top_k=10, user_for_prefs=None):
    current_catalog_with_embeddings = get_catalog_products()
    if not current_catalog_with_embeddings: 
        current_app.logger.error("Product catalog is empty or not loaded in generate_final_recommendations.")
        return [], "Error: Product catalog is critically empty.", {"error": "Product catalog unavailable."}

    openai_description = "N/A (OpenAI not used or no image provided)"
    gemini_refinement_data = {"error": "Gemini not used or input insufficient."}
    visual_recommendations = []
    user_preferences = user_for_prefs.get_preferences() if user_for_prefs and hasattr(user_for_prefs, 'get_preferences') else {}

    if query_image_path:
        if openai_client:
            openai_description = get_image_description_openai(query_image_path, openai_client)
        else:
            current_app.logger.warning("OpenAI client not available for image description.")
            openai_description = "OpenAI client not available for image description."
        
        query_embedding = extract_vit_features(query_image_path)
        if query_embedding is not None:
            db_embeddings_tuples = [(p["embedding"], p) for p in current_catalog_with_embeddings if p.get("embedding") is not None]
            if db_embeddings_tuples:
                db_embeddings = np.array([t[0] for t in db_embeddings_tuples])
                products_with_embeddings = [t[1] for t in db_embeddings_tuples]
                
                similarities = cosine_similarity(query_embedding.reshape(1, -1), db_embeddings)[0]
                sorted_indices = np.argsort(similarities)[::-1]

                for i in sorted_indices:
                    if len(visual_recommendations) < top_k * 2:
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
        current_app.logger.info("No candidate products (visual or catalog) for recommendation.")
        return [], openai_description, gemini_refinement_data

    scored_recommendations = []
    all_search_keywords = set(text_prompt.lower().split())
    all_search_keywords.update(spacy_keywords)

    if isinstance(gemini_refinement_data, dict) and not gemini_refinement_data.get("error"):
        gemini_key_attrs = gemini_refinement_data.get("key_attributes", [])
        gemini_refined_query_terms = gemini_refinement_data.get("refined_search_query", "").lower().split()
        if isinstance(gemini_key_attrs, list): all_search_keywords.update([attr.lower() for attr in gemini_key_attrs])
        all_search_keywords.update(gemini_refined_query_terms)
    all_search_keywords = list(filter(None, all_search_keywords)) 

    for product in candidate_products:
        product_copy = product.copy()
        score = product_copy.get("visual_score", 0.0) * 10.0
        current_reasons = product_copy.get("detailedReasons", [])[:]

        if user_preferences:
            liked_colors = user_preferences.get("liked_colors", {})
            p_colors = [tag.lower() for tag in product_copy.get("color_tags", [])]
            for color, count in liked_colors.items():
                if color in p_colors: score += (count * 0.7)

            interacted_categories = user_preferences.get("interacted_categories", [])
            if product_copy.get("category", "").lower() in [cat.lower() for cat in interacted_categories]:
                score += 2.5
        
        text_match_count = 0
        product_text_corpus = (f"{product_copy.get('name','')} {product_copy.get('description','')} {product_copy.get('type','')} "
                               f"{product_copy.get('category','')} {product_copy.get('style','')} {product_copy.get('material','')} "
                               f"{' '.join(product_copy.get('color_tags',[]))}").lower()
        matched_kw_for_this_product = [kw for kw in all_search_keywords if kw and kw in product_text_corpus]
        text_match_count = len(set(matched_kw_for_this_product))
        score += text_match_count * 2.5

        if text_match_count > 0:
            reason_str = f"Matches: {', '.join(list(set(matched_kw_for_this_product)))}"
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
            
    final_recs_json_safe = []
    for rec_raw in final_recommendations_raw:
        rec_json_safe = rec_raw.copy()
        rec_json_safe["imageUrl"] = rec_json_safe.get("images")[0] if rec_json_safe.get("images") else (rec_json_safe.get("imageUrl") or "/static/placeholder.png")
        base_reason = rec_json_safe.get("recommendationReason", "Recommended")
        final_score_val = rec_json_safe.get('final_score', 0.0)
        
        if final_score_val > 0.01 or "fallback" not in base_reason.lower() :
            rec_json_safe["recommendationReason"] = f"{base_reason} (Score: {final_score_val:.1f})"
        elif "fallback" in base_reason.lower(): rec_json_safe["recommendationReason"] = base_reason
        elif not base_reason or base_reason == "Recommended": rec_json_safe["recommendationReason"] = "Considered (low relevance)"
        
        if "embedding" in rec_json_safe: del rec_json_safe["embedding"]
        if "visual_score" in rec_json_safe: del rec_json_safe["visual_score"]
        
        final_recs_json_safe.append(rec_json_safe)

    return final_recs_json_safe, openai_description, gemini_refinement_data

# --- Main Application Routes ---
@app.route('/')
def index_route(): # Renamed from index
    user_for_prefs = current_user if current_user.is_authenticated else None
    recs, _, _ = generate_final_recommendations(
        text_prompt="trending fashion popular apparel", top_k=8, user_for_prefs=user_for_prefs
    )
    return render_template('index.html', initial_recommendations=json.dumps(recs))

@app.route('/upload_image', methods=['POST'])
def upload_image_route():
    if 'imageFile' not in request.files:
        current_app.logger.warning("Upload attempt: 'imageFile' part missing from request.files")
        return jsonify({"error": "No image file part provided in the request"}), 400
    
    file = request.files['imageFile'] # Assign file object from the request
    
    if not file or not file.filename:
        current_app.logger.warning("Upload attempt: No file selected or filename is empty.")
        return jsonify({"error": "No file selected or filename is empty"}), 400

    # Now `file` is defined. Proceed to check if it's an allowed type.
    if allowed_file(file.filename): # `file` is used here
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath) # `file` is used here
            current_app.logger.info(f"Uploaded image saved to: {filepath}")
            prompt_text = request.form.get('prompt', '')
            user_for_prefs = current_user if current_user.is_authenticated else None
            
            recs_json_safe, openai_desc, gemini_refine = generate_final_recommendations(
                query_image_path=filepath, text_prompt=prompt_text, user_for_prefs=user_for_prefs
            )
            
            image_url_for_preview = url_for('send_uploaded_file', filename=filename)
            
            # Consider deleting filepath if it's large and only needed for this request processing
            # For hackathon, keeping it for send_uploaded_file is simpler.
            # if os.path.exists(filepath):
            #    os.remove(filepath) # If you were to delete it

            return jsonify({
                "message": "Image processed successfully", 
                "filename_server_temp": filename, # The unique name on server
                "image_preview_url": image_url_for_preview, 
                "recommendations": recs_json_safe,
                "openai_description": openai_desc, 
                "gemini_refinement": gemini_refine
            })
        except Exception as e:
            current_app.logger.error(f"Error processing uploaded image route: {e}", exc_info=True)
            if 'filepath' in locals() and os.path.exists(filepath): # Check if filepath was defined
                try: 
                    os.remove(filepath)
                    current_app.logger.info(f"Cleaned up errored upload: {filepath}")
                except Exception as e_rem: 
                    current_app.logger.error(f"Failed to remove temp file {filepath} on error: {e_rem}")
            return jsonify({"error": f"Server error processing image: {str(e)}"}), 500
    else: # This 'else' corresponds to `if allowed_file(file.filename):`
        current_ext = "unknown"
        file_name_log = file.filename # `file` is defined here
        
        if '.' in file.filename: 
            current_ext = file.filename.rsplit('.', 1)[1].lower()
        
        allowed_ext_config = app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
        current_app.logger.warning(f"File type not allowed: {file_name_log} (extension: {current_ext}). Allowed: {', '.join(allowed_ext_config)}")
        return jsonify({"error": f"File type '{current_ext}' not allowed. Please upload one of: {', '.join(allowed_ext_config)}."}), 400


@app.route(f"/{app.config['UPLOAD_FOLDER']}/<path:filename>")
def send_uploaded_file(filename):
    upload_dir = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_dir, filename)


@app.route('/get_recommendations', methods=['POST'])
def get_recommendations_route():
    user_for_prefs = current_user if current_user.is_authenticated else None
    data = request.json
    prompt_text = data.get('prompt', '')
    try:
        recs_json_safe, _, gemini_refine = generate_final_recommendations(
            text_prompt=prompt_text, user_for_prefs=user_for_prefs
        )
        return jsonify({"recommendations": recs_json_safe, "gemini_refinement": gemini_refine})
    except Exception as e:
        current_app.logger.error(f"Error getting text recommendations: {e}", exc_info=True)
        return jsonify({"error": "Failed to get recommendations"}), 500

# --- Authentication Routes ---
@app.route('/api/signup', methods=['POST'])
def signup_api_route():
    if current_user.is_authenticated: return jsonify({"message": "Already logged in"}), 200
    data = request.json
    username = data.get('username')
    email = data.get('email') 
    password = data.get('password')

    if not username or not password: return jsonify({"error": "Username and password required"}), 400
    
    database = db.get_db()
    if not database: return jsonify({"error": "Database unavailable"}), 503

    if User.get_by_username(username): return jsonify({"error": "Username already exists"}), 409
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        cursor = database.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email if email else None, hashed_password)
        )
        database.commit()
        user_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO user_preferences (user_id, preferences_json) VALUES (?, ?)", (user_id, json.dumps({})))
        database.commit()

        new_user_obj = User.get_by_id(str(user_id))
        if new_user_obj:
            login_user(new_user_obj, remember=True)
            return jsonify({"message": "Signup successful!", "user": {"username": new_user_obj.username, "id": new_user_obj.id}}), 201
        return jsonify({"error": "User created but login failed."}), 500
    except sqlite3.IntegrityError as e:
        current_app.logger.warning(f"Signup IntegrityError: {e}")
        return jsonify({"error": "Username or email may already be taken."}), 409
    except Exception as e:
        current_app.logger.error(f"Signup DB error: {e}", exc_info=True)
        return jsonify({"error": "Signup failed due to a server error."}), 500

@app.route('/api/login', methods=['POST'])
def login_api_route():
    if current_user.is_authenticated: return jsonify({"message": "Already logged in"}), 200
    data = request.json; username = data.get('username'); password = data.get('password')
    if not username or not password: return jsonify({"error": "Username and password required"}), 400

    user_obj = User.get_by_username(username)
    if user_obj and user_obj.password_hash and bcrypt.check_password_hash(user_obj.password_hash, password):
        login_user(user_obj, remember=True)
        return jsonify({"message": "Login successful", "user": {"username": user_obj.username, "id": user_obj.id}}), 200
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/logout')
@login_required
def logout_api_route():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

@app.route('/api/current_user_status')
def current_user_status_api_route():
    if current_user.is_authenticated:
        user_obj = User.get_by_id(current_user.id)
        if user_obj:
            return jsonify({
                "logged_in": True,
                "user": {
                    "id": user_obj.id, "username": user_obj.username,
                    "wishlist_ids": user_obj.get_wishlist_ids(),
                    "cart_items_data": user_obj.get_cart_items() # Send items with quantity
                }
            }), 200
        else: logout_user()
    return jsonify({"logged_in": False}), 200

# --- User Data API Routes ---
def get_full_product_details_for_user_list(product_ids_list):
    if not product_ids_list: return []
    all_catalog_products = get_catalog_products()
    details = []
    for prod_id_str in product_ids_list:
        product_detail = next((p.copy() for p in all_catalog_products if str(p['id']) == str(prod_id_str)), None)
        if product_detail:
            if 'embedding' in product_detail: del product_detail['embedding']
            if 'visual_score' in product_detail: del product_detail['visual_score']
            details.append(product_detail)
    return details

@app.route('/api/wishlist', methods=['GET', 'POST', 'DELETE'])
@login_required
def wishlist_api_route():
    user_obj = User.get_by_id(current_user.id)
    if not user_obj: return jsonify({"error": "User not found"}), 404

    if request.method == 'GET':
        wishlist_ids = user_obj.get_wishlist_ids()
        detailed_wishlist = get_full_product_details_for_user_list(wishlist_ids)
        return jsonify({"wishlist": detailed_wishlist}), 200
    
    data = request.json; product_id = str(data.get('productId'))
    if not product_id: return jsonify({"error": "productId required"}), 400

    if request.method == 'POST':
        if user_obj.add_to_wishlist_db(product_id):
            return jsonify({"message": "Added to wishlist", "wishlist_ids": user_obj.get_wishlist_ids()}), 200
    elif request.method == 'DELETE':
        if user_obj.remove_from_wishlist_db(product_id):
            return jsonify({"message": "Removed from wishlist", "wishlist_ids": user_obj.get_wishlist_ids()}), 200
    return jsonify({"error": "Operation failed"}), 500

@app.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
@login_required
def cart_api_route():
    user_obj = User.get_by_id(current_user.id)
    if not user_obj: return jsonify({"error": "User not found"}), 404

    if request.method == 'GET':
        cart_items_data = user_obj.get_cart_items()
        detailed_cart = []
        all_catalog_products = get_catalog_products()
        for item_data in cart_items_data:
            product_detail = next((p.copy() for p in all_catalog_products if str(p['id']) == str(item_data['product_id'])), None)
            if product_detail:
                if 'embedding' in product_detail: del product_detail['embedding']
                if 'visual_score' in product_detail: del product_detail['visual_score']
                product_detail['quantity'] = item_data['quantity']
                detailed_cart.append(product_detail)
        return jsonify({"cart": detailed_cart}), 200
    
    data = request.json; product_id = str(data.get('productId'))
    if not product_id: return jsonify({"error": "productId required"}), 400
    quantity_change = data.get('quantity', 1) # For add, can be >1. For update, could be new total.

    if request.method == 'POST': # Add or update quantity
        if user_obj.add_to_cart_db(product_id, quantity_change): # Modify add_to_cart_db for quantity
            return jsonify({"message": "Cart updated", "cart_items_data": user_obj.get_cart_items()}), 200
    elif request.method == 'DELETE': # Remove entire item
        if user_obj.remove_from_cart_db(product_id):
            return jsonify({"message": "Removed from cart", "cart_items_data": user_obj.get_cart_items()}), 200
    return jsonify({"error": "Operation failed"}), 500

@app.route('/api/preferences/update', methods=['POST'])
@login_required
def update_preferences_api_route():
    data = request.json; action = data.get("action"); value = data.get("value")
    if not action or value is None: return jsonify({"error": "Action and value required"}), 400
    user_obj = User.get_by_id(current_user.id)
    if not user_obj: return jsonify({"error": "User not found"}), 404
    current_preferences = user_obj.get_preferences()

    if action == "liked_color" and isinstance(value, str):
        color = value.lower(); current_preferences.setdefault("liked_colors", {})
        current_preferences["liked_colors"][color] = current_preferences["liked_colors"].get(color, 0) + 1
    elif action == "interacted_category" and isinstance(value, str):
        category = value; current_preferences.setdefault("interacted_categories", [])
        if category not in current_preferences["interacted_categories"]: current_preferences["interacted_categories"].append(category)
        current_preferences["interacted_categories"] = current_preferences["interacted_categories"][-10:]
    elif action == "search_keywords" and isinstance(value, list):
        current_preferences.setdefault("recent_keywords", [])
        for kw in reversed(value): 
            if kw not in current_preferences["recent_keywords"]: current_preferences["recent_keywords"].insert(0, kw)
        current_preferences["recent_keywords"] = current_preferences["recent_keywords"][:10]
    else: return jsonify({"error": "Invalid preference action"}), 400

    if user_obj.save_preferences(current_preferences):
        return jsonify({"message": "Preferences updated", "preferences": current_preferences}), 200
    return jsonify({"error": "Failed to update preferences"}), 500

@app.route('/api/mock_checkout_process', methods=['POST'])
@login_required
def mock_checkout_process_route():
    user_obj = User.get_by_id(current_user.id)
    if not user_obj: return jsonify({"error": "User not found"}), 404
    
    current_cart_items_data = user_obj.get_cart_items()
    if not current_cart_items_data: return jsonify({"error": "Cart is empty"}), 400

    cart_product_details = get_full_product_details_for_user_list([item['product_id'] for item in current_cart_items_data])
    total_price = 0; order_items_summary = []
    for cart_item_spec in current_cart_items_data:
        product_detail = next((p for p in cart_product_details if str(p['id']) == str(cart_item_spec['product_id'])), None)
        if product_detail:
            try:
                price_val = float(str(product_detail.get('price', '0')).replace('$', ''))
                item_total = price_val * cart_item_spec['quantity']
                total_price += item_total
                order_items_summary.append({
                    "id": product_detail.get('id'), "name": product_detail.get('name'), 
                    "price": product_detail.get('price'), "quantity": cart_item_spec['quantity'],
                    "item_total": round(item_total, 2) # round item total
                })
            except ValueError: current_app.logger.warning(f"Price parse error in checkout for {product_detail.get('name')}")
    
    order_str_id = str(uuid.uuid4())
    order_doc = {
        "order_str_id": order_str_id, "user_id": user_obj.id, "items_json": json.dumps(order_items_summary),
        "total_price": round(total_price, 2), "status": "confirmed_mock", "created_at": datetime.utcnow().isoformat()
    }
    
    database = db.get_db()
    if not database: return jsonify({"error": "DB unavailable"}), 503
    try:
        cursor = database.cursor()
        cursor.execute(
            "INSERT INTO orders (order_str_id, user_id, items_json, total_price, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (order_doc["order_str_id"], order_doc["user_id"], order_doc["items_json"], 
             order_doc["total_price"], order_doc["status"], order_doc["created_at"])
        )
        database.commit()
        user_obj.clear_cart_db()
        summary_message = f"Mock order {order_str_id} confirmed! Total: ${total_price:.2f}."
        return jsonify({"message": summary_message, "orderId": order_str_id, "orderItems": order_items_summary, "totalPrice": total_price}), 200
    except sqlite3.Error as e:
        current_app.logger.error(f"Checkout DB error: {e}")
        return jsonify({"error": "Order placement failed."}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)