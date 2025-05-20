# ShopSmarter: AI-Powered Personal Shopping Assistant

ShopSmarter is an AI-powered personal shopping assistant designed to revolutionize the e-commerce experience. Users can upload images of items they like (e.g., a picture from social media, a snapshot of an outfit) or use text prompts to describe what they're looking for. The assistant then analyzes these inputs and provides personalized recommendations for similar or complementary products available on the e-commerce platform.

This project is developed for the Hackathon (Theme 1).

## Features

*   **Image-based Search:** Upload an image to find visually similar products.
*   **Text-based Search & Refinement:** Use natural language prompts to search for products or refine results from an image search.
*   **Product Recommendations:**
    *   Displays similar items based on visual features or text descriptions.
    *   Suggests complementary items (e.g., accessories for an outfit).
*   **Detailed Product View:** Click on a product to see more details, including multiple images, price, description, and why it was recommended.
*   **Wishlist Management:** Add/remove favorite items to a personal wishlist.
*   **Shopping Cart:** Add/remove items to a shopping cart and view a summary.
*   **Mock Checkout:** Simulate a checkout process.
*   **Dark Mode:** Toggle between light and dark themes for user comfort.

*(Note: AI/ML components for image analysis and recommendation are currently mocked for hackathon purposes but designed for future integration.)*

## Tech Stack

*   **Backend:** Python (Flask)
    *   API endpoints for image upload, search, and recommendations.
    *   Serves HTML templates.
*   **Frontend:**
    *   HTML5
    *   CSS3 (Adapted from the original project's `App.css`)
    *   JavaScript (Vanilla JS for DOM manipulation, API calls, and interactivity)
*   **AI/ML (Conceptual - Mocked for now):**
    *   Computer Vision: For analyzing uploaded images (e.g., feature extraction for color, style, category).
    *   NLP: For understanding text prompts.
    *   Recommendation System: To match products based on extracted features and user queries.

## Project Structure
shopsmarter_project/
├── backend_flask/
│ ├── app.py # Flask application
│ ├── requirements.txt # Python dependencies
│ ├── static/
│ │ ├── css/
│ │ │ └── style.css # Main stylesheet
│ │ ├── js/
│ │ │ └── main.js # Main JavaScript file
│ │ └── images/ # For UI assets, favicons etc.
│ ├── templates/
│ │ ├── index.html # Main HTML page
│ │ └── partials/ # Reusable HTML snippets (e.g., _product_card.html)
│ └── uploads/ # Directory for storing uploaded images (add .gitignore)
├── .gitignore
└── README.md

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd shopsmarter_project
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    cd backend_flask
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create an `uploads` directory** inside `backend_flask` if it doesn't exist (this is where uploaded images will be temporarily stored):
    ```bash
    mkdir -p backend_flask/uploads
    ```

5.  **(Optional) For actual AI features (beyond mock):** You might need to download pre-trained models or set up API keys for services like OpenAI CLIP, Google Vision API, etc. This would involve additional setup steps specific to those tools.

## How to Run

1.  **Navigate to the `backend_flask` directory:**
    ```bash
    cd backend_flask
    ```

2.  **Ensure your virtual environment is activated.**

3.  **Run the Flask application:**
    ```bash
    flask run
    # or python app.py
    ```

4.  **Open your web browser** and go to `http://127.0.0.1:5000` (or the address shown in your terminal).

## Development Workflow

1.  **Backend (`app.py`):**
    *   Modify API endpoints for recommendation logic.
    *   Integrate actual AI/ML models for image analysis and text processing.
    *   Update product data sources.
2.  **Frontend (`templates/index.html`, `static/js/main.js`, `static/css/style.css`):**
    *   Adjust HTML structure in `index.html` and partials.
    *   Implement/enhance JavaScript functions in `main.js` for interactivity, API calls, and dynamic content rendering.
    *   Refine styles in `style.css`.

## Submission Guidelines Compliance

*   **Presentation:** A `presentation.pptx` or `presentation.pdf` will be created (max 10-12 slides).
*   **Prototype:** Developed using Python (Flask) for the backend and HTML/CSS/JS for the frontend.
*   **Demo Video:** A video demonstrating the solution will be recorded.
*   **GitHub Link:** The codebase will be available on GitHub.

## Future Scope

*   Integrate real AI models for image feature extraction (color, texture, category, style).
*   Implement a more sophisticated recommendation engine.
*   User accounts and personalized history/preferences.
*   Real-time inventory checks.
*   Automated checkout process with payment gateway integration.