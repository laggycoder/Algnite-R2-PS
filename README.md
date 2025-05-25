# ShopSmarter: AI-Powered Personal Shopping Assistant

ShopSmarter is an advanced, full-featured AI personal shopping assistant prototype. It allows users to discover products through visual search (image upload) or natural language text prompts. The system leverages Vision Transformer (ViT) for visual similarity against a curated product catalog, OpenAI's GPT-4o for rich image descriptions, spaCy for NLP-enhanced query understanding, and Google's Gemini for contextual search refinement and suggestions, including the SQLite database, full user authentication, persistent user data, and the refined AI functionalities.

Dissects uploaded images via OpenAI GPT-4o Vision.
    *   **NLP-Enhanced Textmarter is an advanced AI-powered personal shopping assistant designed to revolutionize the e-commerce experience. Users can upload images Prompts:** spaCy extracts key entities and terms from user text prompts for better search context.
    *   **LLM of items they like or use text prompts for discovery. The assistant leverages a suite of AI models: Vision Transformer (Vi-Powered Query Enhancement:** Google Gemini analyzes image descriptions, user prompts, and spaCy outputs to refine search queries, suggestT) for visual similarity against a curated product catalog, OpenAI's GPT-4o for rich image descriptions, spa key attributes, and even propose complementary item categories.
*   **Intelligent & Personalized Recommendations:**
    *   DisplaysCy for NLP-enhanced query understanding, and Google's Gemini for contextual search refinement and creative suggestions. User accounts, persistent visually similar items by comparing ViT features of the uploaded image against pre-processed embeddings of a local product catalog.
    *    wishlists, carts, and basic preference tracking are managed using an SQLite database.

This project is developed for the Hackathon (Theme 1).

## Core Features

*   **User Authentication & Personalization:**
    *   SecureRecommendations are scored and ranked based on a combination of visual similarity, text relevance (original prompt + NLP/LLM refinements), and basic user preferences (if logged in).
*   **User Accounts & Personalization:**
    *   **User user registration and login (passwords hashed with Bcrypt).
    *   Session management using Flask-Login.
    *    Authentication:** Secure signup, login, and logout functionality using Flask-Login and Bcrypt for password hashing. User data storedPersistent user-specific wishlists and shopping carts stored in an SQLite database.
    *   Basic user preference tracking (e.g., liked colors, interacted categories) stored in SQLite to subtly influence future recommendations.
*   **Multi- in SQLite.
    *   **Persistent Wishlist & Cart:** Logged-in users can save items to theirModal Input & AI Understanding:**
    *   **Image-based Search:** Upload an image to find visually similar products from wishlist and cart, which persist across sessions.
    *   **Basic Preference Learning:** The system tracks simple user interactions (liked a curated local catalog using ViT embeddings.
    *   **AI Image Description:** Get detailed descriptions of uploaded images colors from wishlist/cart, interacted categories) to subtly influence future recommendations.
*   **Interactive User Experience:**
 (apparel, style, color, etc.) using OpenAI GPT-4o Vision.
    *   **NLP-Enhanced Text Prompts:** spaCy assists in extracting key entities and terms from user text prompts.
    *       *   **AI Insights Display:** Shows users the descriptive output from OpenAI Vision and search refinement/keyword suggestions from Gemini**LLM-Powered Query Enhancement:** Google Gemini refines search queries based on image descriptions, user prompts, and spaCy outputs.
    *   **Detailed Product View:** Modal display for product details, including images, price, description, attributes, suggesting key attributes and effective search terms.
*   **Intelligent Product Recommendations:**
    *   Displays visually similar items, and AI-driven "Why Recommended" reasons.
    *   **Mock Checkout Process:** Simulates an order placement by comparing ViT features of the uploaded image against a pre-processed local product catalog.
    *   Suggests complementary flow, storing mock order details for logged-in users.
    *   **Dark Mode:** User-toggleable light item categories based on Gemini's understanding.
    *   Combines visual similarity, AI-generated image descriptions, NLP-extracted keywords, LLM-refined text prompts, and basic user preferences for a comprehensive recommendation score.
*   **Interactive User Experience/dark theme.

## Tech Stack

*   **Backend:** Python (Flask)
    *   Session Management: Flask-Login
    *   Password Hashing: Flask-Bcrypt
*   **Database:** SQLite (managed:**
    *   **AI Insights Display:** Shows users the image description from OpenAI and search refinement suggestions from Gemini.
    *   **Detailed Product View:** Modal display for product details, including AI-driven recommendation reasons.
    * via Python's `sqlite3` module)
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
*   **Core AI/ML Models:**
    *   **Visual Similarity:** Hugging Face `transformers` with   **Mock Checkout:** Simulates an order process, storing mock order details in the SQLite database.
    *   ** Vision Transformer (ViT) (e.g., `google/vit-base-patch16-22Dark Mode:** Toggle between light and dark themes.

## Tech Stack

*   **Backend:** Python (Flask)
    *4-in21k`).
    *   **Image Description:** OpenAI API (`gpt-4o`).
       **Database:** SQLite (managed with Python's `sqlite3` module).
    *   **Authentication:** Flask*   **Language Understanding & Refinement:** Google Generative AI API (`gemini-1.5-flash--Login, Flask-Bcrypt.
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
latest`).
    *   **NLP Preprocessing:** spaCy (`en_core_web_sm`).
**   **Core AI/ML:**
    *   **Visual Similarity:** Hugging Face `transformers` with Vision Transformer (   **Data Source & Preparation:**
    *   Original Dataset: Kaggle "Fashion Product Images (Small)".
ViT) (e.g., `google/vit-base-patch16-224-in    *   Processing Script: `prepare_dataset.py` (Python with Pandas, tqdm) to process raw Kaggle data.21k`).
    *   **Image Description:** OpenAI API (`gpt-4o`).
    *   **Language Understanding & Refinement:** Google Generative AI API (`gemini-1.5-flash-latest`).
    
    *   Curated Catalog: `curated_product_catalog.json` (metadata) and local images in `static/product_images_db/` (for ViT embedding).
*   **Environment:** `*   **NLP Preprocessing:** spaCy (`en_core_web_sm`).
*   **Data Preparationvenv`, `python-dotenv` for API key management.

## Project Structure (Key Components)
```plaintext
Algnite- models.py                   # User class for SQLite and Flask-Login
│   ├── schema.sql                  # SQL schema for SQLite database
│   ├── ai_core/                    # AI specific logic modules
│   │   ├── __init__.py
│   │   ├── vision_models.py        # ViT, OpenAI Vision functions
│   │   ├── languageR2-PS/  (Project Root)
├── backend_flask/
│   ├── app.py                      # Main Flask application, routes, auth logic
│   ├── db.py                       # SQLite database connection and initialization
│   ├──_models.py      # Gemini, spaCy functions
│   │   └── product_catalog.py      # Manages curated models.py                   # User model definition for SQLite
│   ├── schema.sql                  # SQL schema for database tables
│    product data & ViT embeddings
│   ├── static/
│   │   ├── css/style.css
├── ai_core/                    # AI specific logic modules
│   │   ├── __init__.py
│   │   │   ├── js/main.js
│   │   └── product_images_db/      #│   ├── vision_models.py        # ViT, OpenAI Vision functions
│   │   ├── language_models.py LOCAL images for your curated product catalog (committed)
│   ├── templates/index.html
│   ├── uploads/      # Gemini, spaCy functions
│   │   └── product_catalog.py      # Manages curated product data & Vi                    # Temporary user uploads (gitignored)
│   ├── curated_product_catalog.json # Your product metadata "databaseT embeddings
│   ├── static/
│   │   ├── css/style.css
│   │   " (committed)
│   ├── requirements.txt
│   └── .env                        # API Keys & Flask Secret Key├── js/main.js
│   │   └── product_images_db/      # LOCAL images for your (gitignored)
├── kaggle_dataset_raw/             # Raw downloaded Kaggle data (gitignored)
│ curated product catalog
│   ├── templates/
│   │   └── index.html
│   ├── uploads/   ├── images/
│   └── styles.csv
├── prepare_dataset.py              # Script to process Kag                    # Temporary user uploads (gitignored)
│   ├── curated_product_catalog.json # Your product metadatagle data
├── .gitignore
└── README.md
```

## Setup and Installation

1.  **Clone the venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
     repository.**
2.  **Download Kaggle Dataset:**
    *   Create `kaggle_dataset_raw`python -m spacy download en_core_web_sm # Download spaCy English model
    cd .. # in the project root.
    *   Place `styles.csv` into `kaggle_dataset_raw/`. Back to project root
    ```
4.  **Set up API Keys & Flask Secret:**
    *   Create `
    *   Place all individual product image files (e.g., `1163.jpg`) into `kagglebackend_flask/.env` file.
    *   Add your keys:
        ```env
        OPENAI_API__dataset_raw/images/`.
3.  **Set up Backend Environment (inside `backend_flask`):**
KEY="your_openai_api_key_here"
        GOOGLE_API_KEY="your_google_api    ```bash
    cd backend_flask
    python3 -m venv venv
    source venv_key_here"
        FLASK_SECRET_KEY="your_strong_random_generated_secret_key/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    " 
        ```
        *(Generate `FLASK_SECRET_KEY` using `python -c "import secrets;python -m spacy download en_core_web_sm # Download spaCy model
    cd .. # Go back to print(secrets.token_hex(24))"`)*
    *   **Ensure `backend_flask/. project root
    ```
4.  **Set up API Keys & Flask Secret Key:**
    *   Create `backendenv` is in your root `.gitignore`.**
5.  **Prepare Curated Product Catalog:**
    *   Run the_flask/.env` file.
    *   Add your keys:
        ```env
        OPENAI_API_ data preparation script from the project root (`Algnite-R2-PS/`):
        ```bash
        KEY="your_openai_api_key_here"
        GOOGLE_API_KEY="your_google_api_key# Ensure venv is active if pandas/tqdm are installed there
        # backend_flask/venv/bin_here"
        FLASK_SECRET_KEY="your_strong_random_secret_key" 
        ```/python prepare_dataset.py
        python prepare_dataset.py 
        ```
    *   This
        *(Generate FLASK_SECRET_KEY using `python -c "import secrets; print(secrets.token_ creates `backend_flask/curated_product_catalog.json` and copies images to `backend_flask/statichex(24))"`)*
    *   **Ensure `backend_flask/.env` is listed in your root/product_images_db/`.

## How to Run

1.  **Navigate to the project root (`Al `.gitignore`.**
5.  **Prepare Curated Product Catalog & Database:**
    *   Run the data preparation scriptgnite-R2-PS/`).**
2.  **Ensure your virtual environment (`backend_flask/venv from the project root:
        ```bash
        # Ensure venv is active if pandas/tqdm are only`) is activated.**
3.  **Run the Flask application:**
    ```bash
    python -m flask --app backend_flask.app run --no-reload
    ```
    *(Or set `FLASK_APP=backend_ in venv
        # backend_flask/venv/bin/python prepare_dataset.py
        python prepare_flask.app` and then `flask run --no-reload`)*
4.  **Open your web browser** to `dataset.py 
        ```
    *   This creates `backend_flask/curated_product_catalog.json`http://127.0.0.1:5000`.
    *   The first run and copies images to `backend_flask/static/product_images_db/`.
    *   The SQLite (or if `shopsmarter.sqlite3` is deleted) will create the SQLite database and tables.
    * database (`shopsmarter.sqlite3`) and its schema will be automatically created by `app.py` on first   The application startup will also preprocess the product catalog to generate ViT embeddings (monitor terminal logs for progress and success messages).

 run if the file doesn't exist or tables are missing.

## How to Run

1.  **Navigate to the project root (`Algnite-R2-PS/`).**
2.  **Ensure your virtual environment (`## Key AI and Application Logic Flow

1.  **Startup:**
    *   SQLite database (`shopsmarter.sqlitebackend_flask/venv`) is activated.**
    ```bash
    # If not active and you are in project3`) is initialized if not present, using `schema.sql`.
    *   AI models (ViT, spa root:
    # source backend_flask/venv/bin/activate
    ```
3.  **RunCy) are loaded. OpenAI & Gemini clients are configured.
    *   `load_and_preprocess_catalog()` reads `curated_product_catalog.json`, loads images from `static/product_images_db/`, generates the Flask application:**
    ```bash
    python -m flask --app backend_flask.app run --no-reload
    ```
    Alternatively:
    ```bash
    export FLASK_APP=backend_flask.app
    flask run --no-reload
    ```
4.  **Open your web browser** to `http://12 ViT embeddings, and stores the processed catalog in memory.
2.  **User Authentication:** Standard Flask-Login flow7.0.0.1:5000`.
    *   Monitor terminal logs on startup for database with password hashing, storing user data in the `users` SQLite table.
3.  **User Interaction (Image Upload + Optional Prompt):**
    *   User uploads an image; text prompt is optional.
    *   Uploaded initialization and AI model loading, especially the ViT embedding generation for the product catalog.

## Key AI Logic Flow & image is sent to OpenAI (`gpt-4o`) for description.
    *   ViT features are extracted from the uploaded User Features

1.  **Startup:** `app.py` initializes SQLite, AI clients, and calls `load_and_preprocess_catalog()` (from `ai_core.product_catalog`) which generates/loads ViT embeddings for image.
    *   Text prompt (if any) is processed by spaCy.
    *   Image description, spa items in `curated_product_catalog.json`.
2.  **User Authentication:** Users can sign up andCy keywords, and original prompt are sent to Gemini for query refinement.
    *   `generate_final_recommendations` combines:
        *   ViT visual similarity (uploaded image vs. catalog embeddings).
        *   Textual log in. Sessions are managed by Flask-Login. User data, wishlists, and carts are stored in the SQLite DB.
3.  **Image Upload & Search:**
    *   OpenAI GPT-4o describes the uploaded relevance (user prompt, spaCy keywords, Gemini's refined query/attributes vs. catalog metadata).
        * image.
    *   ViT extracts features from the uploaded image.
    *   spaCy processes any accompanying   Basic boost from logged-in user's stored preferences.
    *   Results are ranked and displayed.
4.  **User Data Persistence:** Wishlist, cart items, and preferences are stored in SQLite tables linked to the user ID. API text prompt for keywords.
    *   Gemini refines the search based on all inputs.
    *   `generate_final_recommendations` in `app.py` uses visual similarity (ViT), text matching (spaCy, Gemini endpoints manage these.
5.  **Checkout:** A mock process stores a summary of the order in the `orders` keywords), and logged-in user's preferences to rank products from the catalog.
4.  **Text-Only Search table for the logged-in user and clears their cart.

## Submission Guidelines Compliance

*   **Prototype:** Fully functional prototype:** Similar to image search but without the visual components, relying more on spaCy and Gemini for query understanding.
5. with the described features.
*   **Language:** Python (Flask) for backend, HTML/CSS/JS for frontend.
*   (Presentation and Demo Video to be created separately).

For demo, please contact one of these numbers:  
Ishan - 9769752596  
Hafiz - 9539790357  
Dipayan - 8928315649  
