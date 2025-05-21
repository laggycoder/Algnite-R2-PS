
## Setup and Installation

1.  **Clone the repository:**
    ```bash
    # If you haven't cloned it yet:
    # git clone https://github.com/DipayanDasgupta/ShopSmarter.git Algnite-R2-PS
    # cd Algnite-R2-PS
    ```

2.  **Create and activate a Python virtual environment (inside `backend_flask`):**
    ```bash
    cd backend_flask
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up API Keys:**
    *   Create a file named `.env` inside the `backend_flask` directory (`backend_flask/.env`).
    *   Add your API keys to this file:
        ```env
        OPENAI_API_KEY="your_openai_api_key_here"
        GOOGLE_API_KEY="your_google_api_key_here"
        ```
    *   **Ensure `.env` is listed in your root `.gitignore` file.**

5.  **Prepare Product Images:**
    *   Create the directory `backend_flask/static/product_images/` if it doesn't exist.
    *   Place sample product images (e.g., `red_tshirt.jpg`, `blue_jeans.jpg`) into this folder.
    *   In `backend_flask/app.py`, update the `MOCK_PRODUCTS_DB` list: ensure the `image_path_for_ai` field for each product correctly points to its corresponding local image file in `static/product_images/`. Example: `"image_path_for_ai": "static/product_images/red_tshirt.jpg"`.

## How to Run

1.  **Navigate to the `backend_flask` directory:**
    ```bash
    # Assuming you are in the project root (e.g., Algnite-R2-PS/)
    cd backend_flask
    ```

2.  **Ensure your virtual environment is activated.** (e.g., `source venv/bin/activate`)

3.  **Run the Flask application:**
    ```bash
    python app.py
    ```
    *(The `app.py` is configured with `use_reloader=False` which is good for model loading).*

4.  **Open your web browser** and go to `http://127.0.0.1:5000`.

## Development Workflow & Key AI Logic

1.  **Backend (`app.py`):**
    *   **ViT Embeddings:** On startup, `preprocess_product_database()` loads local product images, extracts feature embeddings using ViT, and stores them in `AI_PRODUCT_DATABASE`.
    *   **Image Upload (`/upload_image`):**
        *   The uploaded image is temporarily saved.
        *   OpenAI GPT-4o describes the image.
        *   ViT extracts features from the uploaded image.
        *   `generate_final_recommendations()` is called:
            *   Calculates cosine similarity between the uploaded image's ViT embedding and product DB embeddings.
            *   Google Gemini refines search based on OpenAI's description and any user text prompt.
            *   Combines visual similarity scores and text/Gemini relevance to rank products.
    *   **Text Search (`/get_recommendations`):**
        *   `generate_final_recommendations()` is called with only a text prompt.
        *   Gemini helps interpret the prompt and suggest keywords.
        *   Recommendations are based on text matching against product data, guided by Gemini's insights.
2.  **Frontend (`templates/index.html`, `static/js/main.js`, `static/css/style.css`):**
    *   `main.js` handles API calls, DOM updates, and displays AI-generated descriptions and refinements in the "AI Insights" section.

## Submission Guidelines Compliance

*   **Presentation:** (To be created)
*   **Prototype:** Developed using Python (Flask) with ViT, OpenAI API, and Google Generative AI API. Frontend with HTML/CSS/JS.
*   **Demo Video:** (To be recorded)
*   **GitHub Link:** Codebase available at repository URLs.

## Future Scope

*   More sophisticated fusion of visual and textual relevance scores.
*   Persistent storage for product database and ViT embeddings (e.g., using a vector database).
*   User accounts and personalized recommendation history.
*   Caching for API responses to reduce costs and latency.
*   Advanced complementary product recommendation logic.