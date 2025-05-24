# ShopSmarter: AI-Powered Personal Shopping Assistant

ShopSmarter is an advanced AI-powered personal shopping assistant designed to revolutionize the e-commerce experience. Users can upload images of items they like or use text prompts. The assistant then leverages Vision Transformer (ViT) for visual similarity against a curated product catalog, OpenAI's GPT-4o for rich image descriptions, spaCy for NLP-enhanced query understanding, and Google's Gemini for contextual search refinement and suggestions.

This project is developed for the Hackathon (Theme 1).

## Features

*   **Multi-Modal Input & Understanding:**
    *   **Image-based Search:** Upload an image to find visually similar products from a curated local catalog using ViT embeddings.
    *   **AI Image Description:** Get detailed descriptions of uploaded images (apparel, style, color, etc.) using OpenAI GPT-4o Vision.
    *   **NLP-Enhanced Text Prompts:** spaCy assists in extracting key entities and terms from user text prompts.
    *   **LLM-Powered Query Enhancement:** Google Gemini refines search queries based on image descriptions, user prompts, and spaCy outputs, suggesting key attributes and effective search terms.
*   **Intelligent Product Recommendations:**
    *   Displays visually similar items by comparing ViT features of the uploaded image against a pre-processed local product catalog.
    *   Suggests complementary item categories based on Gemini's understanding.
    *   Combines visual similarity, AI-generated image descriptions, NLP-extracted keywords, and LLM-refined text prompts for a comprehensive recommendation score.
*   **Interactive User Experience:**
    *   **AI Insights Display:** Shows users the image description from OpenAI and search refinement suggestions from Gemini.
    *   **Detailed Product View:** Modal display for product details, including AI-driven recommendation reasons.
    *   Wishlist & Shopping Cart functionality.
    *   Mock Checkout.
    *   Dark Mode.

## Tech Stack

*   **Backend:** Python (Flask)
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
*   **Core AI/ML:**
    *   **Visual Similarity:** Hugging Face `transformers` with Vision Transformer (ViT) (e.g., `google/vit-base-patch16-224-in21k`).
    *   **Image Description:** OpenAI API (`gpt-4o`).
    *   **Language Understanding & Refinement:** Google Generative AI API (`gemini-1.5-flash-latest`).
    *   **NLP Preprocessing:** spaCy (`en_core_web_sm`).
*   **Data Preparation & Management:**
    *   Dataset Source: Kaggle "Fashion Product Images (Small)".
    *   Processing Script: `prepare_dataset.py` (Python with Pandas) to curate a local product catalog from the Kaggle dataset.
    *   Curated Catalog: `curated_product_catalog.json` stores metadata.
    *   Local Product Images: Stored in `static/product_images_db/` for ViT processing.
*   **Environment:** `venv`, `python-dotenv`.

## Project Structure (Key Parts)
Algnite-R2-PS/ (Project Root)
├── backend_flask/
│ ├── app.py # Main Flask application routes
│ ├── ai_core/ # AI specific logic modules
│ │ ├── init.py
│ │ ├── vision_models.py # ViT, OpenAI Vision functions
│ │ ├── language_models.py # Gemini, spaCy functions
│ │ └── product_catalog.py # Manages curated product data & ViT embeddings
│ ├── static/
│ │ ├── css/style.css
│ │ ├── js/main.js
│ │ └── product_images_db/ # LOCAL images for your curated product catalog (committed to Git)
│ ├── templates/index.html
│ ├── uploads/ # Temporary user uploads (gitignored)
│ ├── curated_product_catalog.json # Your product metadata "database" (committed to Git)
│ ├── requirements.txt
│ └── .env # API Keys (gitignored)
├── kaggle_dataset_raw/ # Raw downloaded Kaggle data (gitignored)
│ ├── images/ # Original Kaggle images (gitignored)
│ └── styles.csv # Original Kaggle CSV (gitignored)
├── prepare_dataset.py # Script to process Kaggle data into curated catalog
├── .gitignore
├── LICENSE
└── README.md

## Setup and Installation

1.  **Clone the repository.**
    ```bash
    # Example:
    # git clone https://github.com/YourUsername/YourRepoName.git Algnite-R2-PS
    # cd Algnite-R2-PS
    ```

2.  **Download Kaggle Dataset:**
    *   Download the "Fashion Product Images (Small)" dataset from Kaggle.
    *   Create a directory `kaggle_dataset_raw` in the project root.
    *   Place `styles.csv` into `kaggle_dataset_raw/`.
    *   Place all individual product image files (e.g., `1163.jpg`) into `kaggle_dataset_raw/images/`.
    *   *(Note: `kaggle_dataset_raw/` is gitignored, so you do this locally).*

3.  **Set up Backend Environment (inside `backend_flask`):**
    ```bash
    cd backend_flask
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm # Download spaCy model
    cd .. # Go back to project root
    ```

4.  **Set up API Keys:**
    *   Create `backend_flask/.env` file.
    *   Add your keys:
        ```env
        OPENAI_API_KEY="your_openai_api_key_here"
        GOOGLE_API_KEY="your_google_api_key_here"
        ```
    *   **Ensure `backend_flask/.env` is listed in your root `.gitignore`.**

5.  **Prepare Curated Product Catalog:**
    *   Run the data preparation script from the project root:
        ```bash
        # Ensure your venv is active if pandas/tqdm were installed there,
        # or if the script needs to import from your project's ai_core (it doesn't currently).
        # backend_flask/venv/bin/python prepare_dataset.py
        # OR if pandas/tqdm are globally accessible:
        python prepare_dataset.py
        ```
    *   This script will:
        *   Read `kaggle_dataset_raw/styles.csv`.
        *   Copy selected images from `kaggle_dataset_raw/images/` to `backend_flask/static/product_images_db/`.
        *   Create `backend_flask/curated_product_catalog.json`.
    *   *(For the hackathon, `curated_product_catalog.json` and images in `static/product_images_db/` are intended to be committed to Git after generation).*

## How to Run

1.  **Navigate to `backend_flask` and activate `venv`.**
    ```bash
    cd backend_flask
    source venv/bin/activate
    ```
2.  **Run the Flask application:**
    ```bash
    python app.py
    ```
3.  **Open your browser** to `http://127.0.0.1:5000`.
    *   The first run after preparing the catalog (or if `precomputed_ai_catalog.pkl` is deleted/outdated) will preprocess the product catalog to generate ViT embeddings. Monitor terminal logs.

## Key AI Logic Flow

1.  **Startup:** `load_and_preprocess_catalog()` (from `ai_core.product_catalog`) reads `curated_product_catalog.json`, loads corresponding local images from `static/product_images_db/`, and generates ViT embeddings for each product. These are stored in memory (or loaded from/saved to `precomputed_ai_catalog.pkl` if implemented).
2.  **User Interaction (Image Upload):**
    *   Uploaded image is sent to OpenAI (`gpt-4o`) for description via `get_image_description_openai`.
    *   ViT features are extracted from the uploaded image via `extract_vit_features`.
    *   User's text prompt (if any) is processed by spaCy via `extract_keywords_spacy`.
    *   OpenAI description, spaCy keywords, and user prompt are sent to Gemini (`gemini-1.5-flash-latest`) for query refinement and complementary ideas via `get_refined_search_gemini`.
    *   `generate_final_recommendations` in `app.py` calculates cosine similarity between uploaded image's ViT embedding and catalog embeddings. It then combines this visual score with text matching scores (derived from user prompt, spaCy, and Gemini's refined query/attributes) against the catalog's textual metadata to produce final ranked recommendations.
3.  **User Interaction (Text-Only Prompt):**
    *   Similar flow, but without the OpenAI description and ViT visual similarity components. Focus is on spaCy and Gemini enhancing the text prompt to search the catalog.

## Submission Guidelines Compliance

*   **Presentation:** (To be created)
*   **Prototype:** Developed using Python (Flask) with ViT, OpenAI API, spaCy, and Google Generative AI API. Frontend with HTML/CSS/JS.
*   **Demo Video:** (To be recorded)
*   **GitHub Link:** This repository.