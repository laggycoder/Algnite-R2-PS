import pandas as pd
import json
import os
import shutil
from tqdm import tqdm # For progress bar, install with: pip install tqdm

# --- Configuration ---
# Paths relative to where this script (prepare_dataset.py) is run from (project root)
KAGGLE_DATA_DIR = "kaggle_dataset_raw"
# IMAGES_ARE_DIRECTLY_IN = os.path.join(KAGGLE_DATA_DIR, "images") # This is where 1163.jpg etc. are
STYLES_CSV_FILE = os.path.join(KAGGLE_DATA_DIR, "styles.csv")

# Output paths (relative to project root, then adjusted for backend_flask)
BACKEND_FLASK_DIR = "backend_flask"
CURATED_CATALOG_JSON_OUTPUT_PATH = os.path.join(BACKEND_FLASK_DIR, "curated_product_catalog.json")
CURATED_IMAGES_DB_DIR_RELATIVE_TO_BACKEND = os.path.join("static", "product_images_db")
CURATED_IMAGES_DB_DIR_ABSOLUTE = os.path.join(BACKEND_FLASK_DIR, CURATED_IMAGES_DB_DIR_RELATIVE_TO_BACKEND)

MAX_PRODUCTS_TO_CURATE = 2000  # Adjust as needed for hackathon performance
# --- End Configuration ---

def ensure_dir_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")

def main():
    print("--- Starting Dataset Preparation (Direct Image Access) ---")

    # Ensure output directories exist
    ensure_dir_exists(BACKEND_FLASK_DIR)
    ensure_dir_exists(CURATED_IMAGES_DB_DIR_ABSOLUTE)
    
    # Path to the directory containing individual Kaggle images
    IMAGES_ARE_DIRECTLY_IN = os.path.join(KAGGLE_DATA_DIR, "images")
    if not os.path.isdir(IMAGES_ARE_DIRECTLY_IN):
        print(f"ERROR: Image directory not found at {IMAGES_ARE_DIRECTLY_IN}. Ensure images are extracted there.")
        return

    # 1. Read styles.csv
    if not os.path.exists(STYLES_CSV_FILE):
        print(f"ERROR: {STYLES_CSV_FILE} not found. Please download it and place it in {KAGGLE_DATA_DIR}/")
        return
    
    print(f"Reading {STYLES_CSV_FILE}...")
    try:
        df = pd.read_csv(STYLES_CSV_FILE, on_bad_lines='warn')
        print(f"Successfully read {len(df)} rows from styles.csv.")
    except FileNotFoundError:
        print(f"Error: {STYLES_CSV_FILE} not found.")
        return
    except Exception as e:
        print(f"Error reading {STYLES_CSV_FILE}: {e}")
        return

    # 2. Curate products and copy images
    print(f"Curating up to {MAX_PRODUCTS_TO_CURATE} products...")
    curated_products_list = []
    added_product_ids = set()

    for _, row in tqdm(df.iterrows(), total=min(len(df), MAX_PRODUCTS_TO_CURATE), desc="Processing products"):
        if len(curated_products_list) >= MAX_PRODUCTS_TO_CURATE:
            break

        product_id_csv = str(row['id']) # ID from CSV
        if product_id_csv in added_product_ids:
            continue

        original_image_filename = f"{product_id_csv}.jpg"
        path_to_original_image = os.path.join(IMAGES_ARE_DIRECTLY_IN, original_image_filename)

        if os.path.exists(path_to_original_image):
            target_image_filename_in_db = f"{product_id_csv}.jpg"
            absolute_target_image_path = os.path.join(CURATED_IMAGES_DB_DIR_ABSOLUTE, target_image_filename_in_db)
            
            try:
                shutil.copy2(path_to_original_image, absolute_target_image_path)
            except Exception as e_copy:
                print(f"Warning: Could not copy {path_to_original_image} to {absolute_target_image_path}: {e_copy}")
                continue

            image_path_for_ai_relative_to_backend = os.path.join(CURATED_IMAGES_DB_DIR_RELATIVE_TO_BACKEND, target_image_filename_in_db).replace("\\", "/")
            web_image_path = "/" + image_path_for_ai_relative_to_backend # Starts with /static/

            base_color_str = str(row.get('baseColour', '')).lower() if pd.notna(row.get('baseColour')) else ""
            color_tags_list = [color.strip() for color in base_color_str.split() if color.strip()]
            # Add the full baseColor as a tag if it's multi-word and wasn't split
            if " " in base_color_str and base_color_str not in color_tags_list:
                color_tags_list.append(base_color_str)
            color_tags_list = list(set(color_tags_list)) # Unique tags

            product_entry = {
                "id": product_id_csv,
                "name": str(row.get('productDisplayName', f"Item {product_id_csv}")),
                "price": f"${(abs(hash(product_id_csv)) % 90) + 10}.99",
                "description": str(row.get('productDisplayName', "")) + f". Gender: {row.get('gender', 'N/A')}, Color: {row.get('baseColour', 'N/A')}, Usage: {row.get('usage', 'N/A')}, Season: {row.get('season', 'N/A')}.",
                "type": str(row.get('articleType', 'Unknown')),
                "category": str(row.get('masterCategory', 'Unknown')),
                "subCategory": str(row.get('subCategory', 'Unknown')),
                "style": str(row.get('usage', 'N/A')),
                "material": "Assorted", # Placeholder
                "color_tags": color_tags_list,
                "gender": str(row.get('gender', 'Unisex')),
                "season": str(row.get('season', 'All Seasons')),
                "year": str(row.get('year', 'N/A')),
                "image_path_for_ai": image_path_for_ai_relative_to_backend,
                "images": [web_image_path],
                "embedding": None
            }
            curated_products_list.append(product_entry)
            added_product_ids.add(product_id_csv)
        else:
            # This might happen if an ID in styles.csv doesn't have a corresponding image file
            # print(f"Info: Image for product ID {product_id_csv} not found at {path_to_original_image}. Skipping.")
            pass
            
    # 3. Save the curated catalog to JSON
    print(f"Saving {len(curated_products_list)} curated products to {CURATED_CATALOG_JSON_OUTPUT_PATH}...")
    try:
        with open(CURATED_CATALOG_JSON_OUTPUT_PATH, 'w') as f:
            json.dump(curated_products_list, f, indent=2)
        print("Curated product catalog saved successfully.")
    except Exception as e:
        print(f"Error saving curated catalog JSON: {e}")
        return
    
    print(f"--- Dataset Preparation Complete ---")
    print(f"Make sure to review '{CURATED_CATALOG_JSON_OUTPUT_PATH}' and the images in '{CURATED_IMAGES_DB_DIR_ABSOLUTE}'.")

if __name__ == "__main__":
    main()