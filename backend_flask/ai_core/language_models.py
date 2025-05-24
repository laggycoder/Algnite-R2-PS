# backend_flask/ai_core/language_models.py
import os
import json
import google.generativeai as genai
import spacy
from flask import current_app

# spaCy Model Loading (Load once)
nlp_spacy = None

def load_spacy_model():
    global nlp_spacy
    if nlp_spacy is None:
        try:
            current_app.logger.info("Loading spaCy model (en_core_web_sm)...")
            nlp_spacy = spacy.load("en_core_web_sm") # Small English model
            current_app.logger.info("spaCy model loaded successfully.")
        except OSError: # Model not downloaded
            current_app.logger.warning("spaCy model 'en_core_web_sm' not found. Please download it by running: python -m spacy download en_core_web_sm")
            current_app.logger.warning("spaCy NLP features will be limited.")
        except Exception as e:
            current_app.logger.error(f"Error loading spaCy model: {e}")
    return nlp_spacy

def extract_keywords_spacy(text):
    nlp = load_spacy_model()
    if not nlp or not text:
        return []
    
    doc = nlp(text.lower())
    keywords = set()
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop and len(token.lemma_) > 2:
            keywords.add(token.lemma_)
    for ent in doc.ents:
        if ent.label_ in ["PRODUCT", "ORG", "WORK_OF_ART"]:
            keywords.add(ent.text.lower())
            
    current_app.logger.info(f"spaCy extracted keywords: {list(keywords)} from text (snippet): {text[:50]}...")
    return list(keywords)


def get_refined_search_gemini(image_description, user_prompt, product_context_str=""):
    # Corrected: Remove the genai._configured check.
    # The configuration is done in app.py and GenAI calls will fail if not configured.
    # You can add a check for the API key environment variable if desired for an earlier warning.
    if not os.getenv("GOOGLE_API_KEY"):
        current_app.logger.warning("GOOGLE_API_KEY environment variable not found. Gemini API call will likely fail.")
        # Return an error structure consistent with other error returns from this function
        return {"error": "Gemini API key not configured in environment."}

    try:
        gemini_model_name = "gemini-1.5-flash-latest" # Or "gemini-1.5-pro-latest"
        # Ensure genai.configure() was called in app.py before this point.
        # The SDK should use the globally configured API key.
        model = genai.GenerativeModel(gemini_model_name)
        current_app.logger.info(f"Using Gemini model for refinement: {gemini_model_name}")
        
        prompt_template = f"""
        You are an AI shopping assistant helping a user find products based on an image and a text query.
        Image Description (from Vision AI): "{image_description}"
        User's Text Query: "{user_prompt}"
        Context from visually similar items (if any): "{product_context_str}"

        Analyze all available information and provide a structured JSON response with ONLY the following keys:
        1.  "key_attributes": A list of 3-7 specific, searchable attributes or features derived from the inputs (e.g., "red floral dress", "leather ankle boots", "minimalist silver necklace", "summer casual").
        2.  "refined_search_query": A single, optimized search query string (max 10 words) that could be used directly in an e-commerce search bar.
        3.  "complementary_item_categories": A list of 1-3 general categories of items that would complement the main described item (e.g., "handbags", "scarves", "belts", "shoes" if main is a dress).
        4.  "confidence_level": Your confidence (Low, Medium, High) that you've understood the user's core need.
        5.  "user_intent_summary": A very brief (1 sentence) summary of what you think the user is looking for.

        Example JSON output:
        {{
          "key_attributes": ["vintage floral print", "midi dress", "long sleeve", "bohemian style"],
          "refined_search_query": "long sleeve vintage floral midi dress boho",
          "complementary_item_categories": ["ankle boots", "wide-brim hat", "crossbody bag"],
          "confidence_level": "High",
          "user_intent_summary": "User is looking for a bohemian-style floral midi dress with long sleeves."
        }}

        If the input is very vague, make the attributes broader and the confidence lower.
        Prioritize generating good "key_attributes" and "refined_search_query".
        Output ONLY the JSON object.
        """
        
        response = model.generate_content(prompt_template)
        
        try:
            cleaned_response_text = response.text.strip()
            if cleaned_response_text.startswith("```json"):
                cleaned_response_text = cleaned_response_text[7:]
            if cleaned_response_text.startswith("```"):
                cleaned_response_text = cleaned_response_text[3:]
            if cleaned_response_text.endswith("```"):
                cleaned_response_text = cleaned_response_text[:-3]
            cleaned_response_text = cleaned_response_text.strip()

            gemini_output = json.loads(cleaned_response_text)
            current_app.logger.info(f"Gemini Refinement Output (parsed): {gemini_output}")
            return gemini_output
        except json.JSONDecodeError as e_json:
            current_app.logger.warning(f"Gemini response was not valid JSON after cleaning. Error: {e_json}. Raw text: {response.text}")
            return {"raw_text": response.text, "error": "Gemini response format issue. Returned raw text."}
        except Exception as e_parse:
            current_app.logger.error(f"Unexpected error parsing Gemini response: {e_parse}. Raw text: {response.text}")
            return {"raw_text": response.text, "error": f"Gemini parsing error: {str(e_parse)}"}

    except Exception as e:
        # This will catch errors from genai.GenerativeModel() if API key wasn't configured,
        # or other API call issues.
        current_app.logger.error(f"Error with Gemini API call in language_models: {e}")
        return {"error": f"Error interacting with Gemini: {str(e)}"}