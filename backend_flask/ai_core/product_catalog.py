# backend_flask/ai_core/product_catalog.py
import json
import os
from flask import current_app
from .vision_models import extract_vit_features # For ViT embeddings

DB_METADATA_FILE = "curated_product_catalog.json"
DB_IMAGE_FOLDER_RELATIVE = os.path.join("static", "product_images_db") # Relative to backend_flask
AI_PRODUCT_CATALOG = [] # This will hold products with embeddings

def load_and_preprocess_catalog():
    """
    Loads product data from a JSON file and computes ViT embeddings for their local images.
    This should be called once on app startup.
    """
    global AI_PRODUCT_CATALOG
    AI_PRODUCT_CATALOG = [] # Reset
    
    # ViT model must be loaded first (done in app.py's app_context)
    # We'll assume extract_vit_features will work if models are loaded.

    catalog_file_path = os.path.join(current_app.root_path, DB_METADATA_FILE)
    current_app.logger.info(f"Attempting to load product catalog from: {catalog_file_path}")

    try:
        with open(catalog_file_path, 'r') as f:
            raw_products = json.load(f)
        current_app.logger.info(f"Loaded {len(raw_products)} raw products from {DB_METADATA_FILE}")
    except FileNotFoundError:
        current_app.logger.error(f"{DB_METADATA_FILE} not found. Cannot populate product catalog.")
        return
    except json.JSONDecodeError:
        current_app.logger.error(f"Error decoding JSON from {DB_METADATA_FILE}.")
        return

    processed_count = 0
    for product_data in raw_products:
        product = product_data.copy() # Work with a copy
        
        # Image path for ViT embedding (relative to backend_flask)
        # Assumes 'image_path_for_ai' in JSON is like "static/product_images_db/image.jpg"
        rel_image_path = product.get('image_path_for_ai')
        abs_image_path_for_ai = None

        if rel_image_path:
            abs_image_path_for_ai = os.path.join(current_app.root_path, rel_image_path)
        
        if abs_image_path_for_ai and os.path.exists(abs_image_path_for_ai):
            embedding = extract_vit_features(abs_image_path_for_ai)
            if embedding is not None:
                product["embedding"] = embedding
                processed_count += 1
            else:
                product["embedding"] = None
                current_app.logger.warning(f"Failed to get ViT embedding for {product.get('name', 'Unknown Product')} (Path: {abs_image_path_for_ai})")
        else:
            product["embedding"] = None
            current_app.logger.warning(f"Image for ViT not found or path missing for {product.get('name', 'Unknown Product')}. Path checked: {abs_image_path_for_ai}")

        # Ensure 'images' (for frontend) uses a web-accessible path
        if isinstance(product.get("images"), list) and product["images"]:
            # If image_path_for_ai is "static/...", then images[0] should also be "/static/..."
            product["imageUrl"] = product["images"][0] # Use the first image for card display
            if not product["imageUrl"].startswith("/static/"):
                current_app.logger.warning(f"Product '{product.get('name')}' images[0] path '{product['imageUrl']}' may not be web accessible. Should start with /static/")
        elif product.get("image_path_for_ai") and product["image_path_for_ai"].startswith("static/"):
             product["imageUrl"] = "/" + product["image_path_for_ai"] # Make it web accessible
        else:
            product["imageUrl"] = "/static/placeholder_no_image.png" # Fallback

        AI_PRODUCT_CATALOG.append(product)
    
    current_app.logger.info(f"Finished catalog preprocessing. {processed_count}/{len(AI_PRODUCT_CATALOG)} products have ViT embeddings.")
    if processed_count == 0 and len(AI_PRODUCT_CATALOG) > 0:
        current_app.logger.warning("No products were successfully embedded with ViT. Check image paths and ViT model loading.")

def get_catalog_products():
    """Returns the processed product catalog."""
    return AI_PRODUCT_CATALOG

# You can add search functions here later, e.g., search_by_keywords, get_similar_by_embedding