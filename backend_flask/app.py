import os
import uuid
import json
from flask import Flask, request, jsonify, render_template, url_for
from werkzeug.utils import secure_filename
# from PIL import Image # For basic image processing if needed

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Mock Product Database ---
# In a real app, this would come from a database or a more complex system
MOCK_PRODUCTS_DB = [
    {"id": "prod1", "name": "Classic Red T-Shirt", "price": "$19.99", "type": "similar", "description": "A comfortable and stylish red t-shirt.", "images": [f"https://via.placeholder.com/400x450/FF6347/FFFFFF?Text=RedTee1", f"https://via.placeholder.com/400x450/CD5C5C/FFFFFF?Text=RedTee2"], "sizes": ["S", "M", "L"], "colors": ["Red", "Dark Red"], "detailedReasons": ["Matches color 'Red'", "Category: T-Shirt", "Style: Casual"]},
    {"id": "prod2", "name": "Blue Denim Jeans", "price": "$49.99", "type": "complementary", "description": "Perfectly fitting blue denim jeans.", "images": [f"https://via.placeholder.com/400x450/1E90FF/FFFFFF?Text=BlueJeans1"], "sizes": ["28", "30", "32", "34"], "colors": ["Blue"], "detailedReasons": ["Pairs with 'Red T-Shirt'", "Category: Jeans", "Material: Denim"]},
    {"id": "prod3", "name": "Stylish Sneakers", "price": "$79.00", "type": "similar", "description": "Comfortable and trendy sneakers.", "images": [f"https://via.placeholder.com/400x450/D3D3D3/000000?Text=Sneakers1", f"https://via.placeholder.com/400x450/A9A9A9/FFFFFF?Text=Sneakers2"], "sizes": ["8", "9", "10", "11"], "colors": ["Grey", "Black"], "detailedReasons": ["Similar style to casual wear", "Often bought with T-shirts"]},
    {"id": "prod4", "name": "Summer Floral Dress", "price": "$65.00", "type": "similar", "description": "Light and airy floral dress for summer.", "images": [f"https://via.placeholder.com/400x450/FFC0CB/000000?Text=FloralDress1"], "sizes": ["S", "M", "L"], "colors": ["Pink Floral", "Blue Floral"], "detailedReasons": ["Vibe: Summer", "Pattern: Floral"]},
    {"id": "prod5", "name": "Leather Belt", "price": "$25.00", "type": "complementary", "description": "Classic leather belt.", "images": [f"https://via.placeholder.com/400x450/8B4513/FFFFFF?Text=Belt1"], "sizes": ["One Size"], "colors": ["Brown", "Black"], "detailedReasons": ["Accessory for Jeans", "Material: Leather"]},
    {"id": "prod6", "name": "Comfy Hoodie", "price": "$55.99", "type": "similar", "description": "A very comfortable hoodie for cool evenings.", "images": [f"https://via.placeholder.com/400x450/B0C4DE/000000?Text=Hoodie1"], "sizes": ["S", "M", "L", "XL"], "colors": ["Light Blue", "Grey"], "detailedReasons": ["Category: Hoodie", "Style: Casual", "Feature: Soft Fabric"]},
]

def generate_mock_recommendations(image_filename=None, text_prompt=None, context="initial"):
    """
    Generates mock recommendations.
    In a real app, this would involve AI/ML models.
    """
    num_to_generate = 6 + (hash(image_filename or text_prompt or "initial") % 3) # Vary count slightly
    
    # Simple logic for mocking
    results = []
    base_products_copy = [p.copy() for p in MOCK_PRODUCTS_DB] # Work with copies

    for i in range(num_to_generate):
        product_template = base_products_copy[i % len(base_products_copy)]
        
        # Create a unique ID for this instance if needed, or just use template's
        # For this mock, we'll just use the template ID and vary other fields slightly for demo
        
        new_product = product_template.copy() # Ensure it's a copy
        new_product["id"] = f"{product_template['id']}_{context}_{i}" # Make ID unique per call
        
        reason_parts = []
        if context == "initial":
            new_product["name"] = f"Featured: {product_template['name']}"
            reason_parts.append("Popular choice")
        elif image_filename:
            short_name = image_filename.split('.')[0][:10]
            new_product["name"] = f"Match for '{short_name}': {product_template['name']}"
            reason_parts.append(f"Visually similar to {short_name}")
        elif text_prompt:
            short_prompt = text_prompt[:15]
            new_product["name"] = f"For '{short_prompt}...': {product_template['name']}"
            reason_parts.append(f"Matches prompt: '{short_prompt}...'")

        if text_prompt and image_filename:
             reason_parts.append(f"and prompt '{text_prompt[:10]}...'")
        
        new_product["recommendationReason"] = ". ".join(reason_parts) if reason_parts else "Recommended for you."
        
        # Ensure imageUrl is dynamic if using placeholders like via.placeholder.com
        # For this mock, we use the predefined images from MOCK_PRODUCTS_DB
        # but if you were generating new placeholder URLs:
        # new_product["imageUrl"] = f"https://via.placeholder.com/260x250/{(hash(new_product['id']) % 0xFFFFFF):06X}/FFF?Text={new_product['name'][:10].replace(' ', '')}"
        # For this specific mock, we will take the first image from the `images` list as `imageUrl`
        if new_product.get("images"):
            new_product["imageUrl"] = new_product["images"][0]
        else: # Fallback if "images" list is missing or empty
            new_product["imageUrl"] = f"https://via.placeholder.com/260x250/CCCCCC/000000?Text=NoImage"


        results.append(new_product)
        
    return results[:num_to_generate] # Trim to desired count

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_image_mock(filepath):
    """
    Mock image analysis.
    In a real app, this would call a CV model.
    """
    # For demo, could extract basic info from filename or just return generic features
    # from PIL import Image
    # img = Image.open(filepath)
    # features = {"width": img.width, "height": img.height, "format": img.format}
    features = {"colors": ["red", "blue"], "style": "casual"} # Mock features
    print(f"Mock analyzing image: {filepath}. Features: {features}")
    return features

# --- Routes ---
@app.route('/')
def index():
    initial_recs = generate_mock_recommendations(context="initial")
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
            # image_features = analyze_image_mock(filepath) # Placeholder for actual analysis

            # For the frontend to display the uploaded image:
            image_url = url_for('static', filename=f'../{UPLOAD_FOLDER}/{filename}')
            
            # Generate recommendations based on the uploaded image
            prompt_text = request.form.get('prompt', '') # Get prompt if sent with image
            recommendations = generate_mock_recommendations(image_filename=filename, text_prompt=prompt_text, context="image")
            
            return jsonify({
                "message": "Image uploaded successfully", 
                "filename": filename,
                "filepath_url": image_url, # URL to display the uploaded image
                "recommendations": recommendations
            })
        except Exception as e:
            app.logger.error(f"Error processing uploaded image: {e}")
            return jsonify({"error": f"Server error processing image: {str(e)}"}), 500
        # finally:
            # Optionally, delete the file after processing if it's not needed long-term
            # os.remove(filepath) 
    else:
        return jsonify({"error": "File type not allowed"}), 400

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations_route():
    data = request.json
    prompt_text = data.get('prompt', '')
    image_filename = data.get('image_filename') # If an image was previously uploaded

    if not prompt_text and not image_filename:
        return jsonify({"error": "Either a prompt or an image context is required"}), 400

    try:
        # Here, you'd integrate your AI/ML logic
        # For now, we use the mock function
        if image_filename and prompt_text:
            context = "image_prompt"
        elif image_filename:
            context = "image"
        else:
            context = "prompt"
            
        recommendations = generate_mock_recommendations(image_filename=image_filename, text_prompt=prompt_text, context=context)
        return jsonify({"recommendations": recommendations})
    except Exception as e:
        app.logger.error(f"Error getting recommendations: {e}")
        return jsonify({"error": "Failed to get recommendations"}), 500

@app.route('/mock_checkout', methods=['POST'])
def mock_checkout_route():
    data = request.json
    cart_items = data.get('cartItems', [])
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400
    
    total_price = 0
    summary_items = []
    for item in cart_items:
        try:
            price = float(item.get('price', '$0').replace('$', ''))
            total_price += price
            summary_items.append(f"{item.get('name', 'Unknown Item')} ({item.get('price', '$0')})")
        except ValueError:
            # Handle cases where price might not be a valid float
            app.logger.warning(f"Could not parse price for item: {item.get('name')}")

    summary_message = f"Checkout successful for {len(cart_items)} items. Total: ${total_price:.2f}.\nItems:\n- " + "\n- ".join(summary_items)
    app.logger.info(f"Mock Checkout: {summary_message}")
    return jsonify({"message": summary_message, "totalItems": len(cart_items), "totalPrice": f"${total_price:.2f}"})


if __name__ == '__main__':
    app.run(debug=True)