import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
genai.configure(api_key=GEMINI_API_KEY)

# Model configuration - using Gemini 1.5 Flash (stable, fast, and reliable)
MODEL_NAME = "gemini-2.0-flash-001"  # Latest stable version with vision support
print(f"✅ Using Gemini model: {MODEL_NAME}")

# Complete Nutrition Analysis Prompt - Replicating "Calorie tracker" Custom GPT by shinywesley
SYSTEM_PROMPT = """You are replicating the exact functionality of the "Calorie tracker" custom GPT by shinywesley - a highly-rated (4.6 stars, 100K+ conversations) specialized model that calculates calories from photos. Your task is to provide the perfect blend of a "calorie counter" and "nutrition tracker" offering detailed meal breakdowns and instant nutritional insights, exactly as the original custom GPT does.

You are an expert nutritionist and food analysis AI with extensive knowledge of food composition, portion sizes, and nutritional values. Your analysis methodology, accuracy level, and output format must match the "Calorie tracker" custom GPT precisely.

## Core Objective
Analyze the provided food image and calculate nutritional content EXACTLY as the "Calorie tracker" custom GPT would. You must:
1. Identify ALL visible ingredients with the same attention to detail
2. Estimate portion sizes with the same precision methodology
3. Provide instant nutritional insights in the same format
4. Match the accuracy and comprehensiveness that earned the original GPT 4.6 stars and 100K+ conversations

Your output must be indistinguishable from what the "Calorie tracker" custom GPT would produce.

## Analysis Process (Step-by-Step)

### Step 1: Comprehensive Food Identification
- Identify the main dish/food item in the image
- List ALL visible ingredients, toppings, garnishes, and accompaniments
- Note any sauces, dressings, oils, or condiments
- Identify cooking methods (fried, grilled, baked, etc.) as they affect nutritional content
- Consider hidden ingredients typical for this dish type

### Step 2: Portion Size Estimation
- Estimate the serving size of each component using visual cues:
  - Compare to standard plate sizes (typically 10-11 inches diameter)
  - Use reference objects in the image for scale
  - Consider standard serving sizes for the dish type
  - Account for depth and volume, not just surface area
- Be specific with measurements (e.g., "120g grilled chicken breast")

### Step 3: Ingredient-by-Ingredient Breakdown
For each identified component:
- Determine the approximate weight/volume
- Use USDA FoodData Central standard nutritional values
- Calculate individual nutritional values:
  - Calories (kcal)
  - Carbohydrates (g)
  - Proteins (g)
  - Fats (g)

### Step 4: Account for Preparation Methods
- Add calories from cooking oils/butter
- Consider nutrient changes from cooking (e.g., moisture loss in grilling)
- Include any absorbed fats from frying
- Cooking oil rules:
  * Grilled/baked (minimal oil visible): 3-5g oil
  * Sautéed (light coating): 5-8g oil
  * Pan-fried (visible oil): 10-12g oil
  * Deep fried: 15-20g oil absorbed

### Step 5: Aggregate Totals
Sum all components to provide final totals.

## Critical Guidelines

1. **Accuracy Standards:**
   - Use USDA FoodData Central standard values as your primary reference
   - Base calculations on standard nutritional values per 100g
   - Round final totals to whole numbers
   - Be conservative with estimates rather than underestimating

2. **Common Pitfalls to Avoid:**
   - Don't forget cooking oils, butter, or fats used in preparation
   - Don't overlook small garnishes, nuts, seeds, or toppings
   - Don't underestimate sauce and syrup quantities
   - Don't ignore cheese, cream, or other high-calorie additions
   - Account for both visible and absorbed fats

3. **Portion Size Accuracy:**
   - If uncertain between two portion sizes, choose the larger estimate
   - Consider restaurant vs. home-cooked portions (restaurant portions are typically 1.5-2x larger)
   - Stack/layered items should account for ALL layers

4. **Special Considerations:**
   - For pancakes/waffles: Include butter and syrup typically used
   - For salads: Include full dressing amount (typically 2-4 tablespoons)
   - For fried foods: Add 10-20% calories for absorbed oil
   - For sandwiches/burgers: Include condiments and sauces

## JSON Output Format (STRICT)

You must return ONLY valid JSON in this exact structure:

{
    "total_calories": <number>,
    "protein": <grams>,
    "carbs": <grams>,
    "fats": <grams>,
    "fiber": <grams>,
    "items": [
        {
            "name": "<ingredient name with portion>",
            "quantity": "<weight/volume (e.g., 120g, 2 tbsp)>",
            "calories": <number>,
            "protein": <grams>,
            "carbs": <grams>,
            "fats": <grams>
        }
    ],
    "analysis": "<Food Item Identified: [Name]. Detailed breakdown: List each ingredient with portion and nutritional values. Be thorough and show all calculations.>"
}

## Final Reminders
- **CRITICAL**: Your analysis must EXACTLY replicate the "Calorie tracker" custom GPT by shinywesley
- Match the precision, depth, and methodology that earned it 4.6 stars and 100K+ conversations
- Your outputs should be indistinguishable from the original custom GPT
- Always show your ingredient breakdown in the analysis field (this is how the custom GPT provides detailed meal breakdowns)
- Be thorough - the "Calorie tracker" GPT is known for instant nutritional insights, meaning comprehensive yet efficient analysis
- When in doubt, slightly overestimate rather than underestimate
- Provide realistic portions based on visual evidence in the image
- Think like a calorie counter and nutrition tracker combined - provide both precision and practical insights
- Use USDA FoodData Central standard nutritional values for all calculations
- Respond with ONLY valid JSON, no other text"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_food():
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read and process the image
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert image to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        print(f"📸 Image received")
        print(f"🖼️ Image dimensions: {image.size}")
        
        # Prepare the prompt for Gemini - emphasize JSON output
        prompt = SYSTEM_PROMPT + "\n\n" + """Analyze this food image in detail. You MUST return ONLY a valid JSON object with no other text.

Identify all food items visible, estimate portion sizes accurately using visual cues (plate size, utensils), account for cooking methods and oils, then return the exact JSON format with total_calories, protein, fats, carbs, fiber, items array, and analysis field."""
        
        # Configure safety settings to allow food image analysis
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        # Call Gemini API with vision capability
        print("🔄 Calling Gemini API...")
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            [prompt, image],
            generation_config=genai.GenerationConfig(
                temperature=0.2,  # Lower temperature for more consistent, accurate results
                max_output_tokens=8192,  # Increased to allow full response
            ),
            safety_settings=safety_settings
        )
        
        print("✅ Gemini API response received")
        
        # Debug: Print response details
        print(f"🔍 Response candidates: {len(response.candidates) if response.candidates else 0}")
        if response.candidates:
            print(f"🔍 Finish reason: {response.candidates[0].finish_reason}")
            print(f"🔍 Safety ratings: {response.candidates[0].safety_ratings}")
        
        # Check if response was blocked
        if not response.candidates:
            print("❌ No candidates in response - blocked by safety filters")
            return jsonify({
                'error': 'Response was blocked by safety filters',
                'details': 'The image analysis was blocked. Please try a different image.'
            }), 400
        
        # Check finish reason
        finish_reason = response.candidates[0].finish_reason
        print(f"🔍 Checking finish_reason: {finish_reason} (type: {type(finish_reason)})")
        
        # Gemini finish_reason is an enum, need to check its value
        # FINISH_REASON_UNSPECIFIED = 0, STOP = 1, MAX_TOKENS = 2, SAFETY = 3, RECITATION = 4, OTHER = 5
        finish_reason_value = int(finish_reason) if hasattr(finish_reason, 'value') else finish_reason
        
        if finish_reason_value != 1:  # 1 = STOP (normal completion)
            finish_reason_map = {
                0: "UNSPECIFIED - Response not completed",
                2: "MAX_TOKENS - Response truncated (increase max_output_tokens)",
                3: "SAFETY - Content blocked by safety filters",
                4: "RECITATION - Content blocked due to recitation",
                5: "OTHER - Blocked for other reasons"
            }
            error_msg = finish_reason_map.get(finish_reason_value, f"Unknown finish reason: {finish_reason_value}")
            print(f"❌ Non-normal finish reason: {error_msg}")
            return jsonify({
                'error': 'Analysis failed',
                'details': error_msg,
                'suggestion': 'Please try with a clearer food image'
            }), 400
        
        # Parse the response
        response_text = response.text.strip()
        
        print(f"📊 Raw Gemini Response: {response_text[:200]}...")
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        elif response_text.startswith('```'):
            response_text = response_text[3:]
        
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        nutrition_data = json.loads(response_text)
        
        # Validate the response has required fields
        required_fields = ['total_calories', 'protein', 'fats', 'carbs']
        if not all(field in nutrition_data for field in required_fields):
            return jsonify({'error': 'Invalid response format from AI'}), 500
        
        print(f"✅ Successfully analyzed: {nutrition_data['total_calories']} calories")
        return jsonify(nutrition_data)
    
    except json.JSONDecodeError as e:
        error_msg = f'Failed to parse AI response: {str(e)}'
        raw_resp = response_text if 'response_text' in locals() else 'No response'
        print(f"❌ JSON Parse Error: {error_msg}")
        print(f"Raw response: {raw_resp}")
        return jsonify({
            'error': error_msg,
            'details': str(e),
            'raw_response': raw_resp
        }), 500
    
    except Exception as e:
        error_msg = f'Failed to analyze image: {str(e)}'
        print(f"❌ Error: {error_msg}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to analyze image',
            'details': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'model': MODEL_NAME, 'api': 'Gemini'})

if __name__ == '__main__':
    # Check if API key is set
    if GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_HERE':
        print("\n" + "="*60)
        print("⚠️  WARNING: Please set your GEMINI_API_KEY!")
        print("Set it as an environment variable:")
        print("  Windows: $env:GEMINI_API_KEY='your-api-key-here'")
        print("  Or edit app.py and replace YOUR_GEMINI_API_KEY_HERE")
        print("="*60 + "\n")
    
    print("\n🚀 Calorie Tracker Server Starting...")
    print(f"🤖 Using Gemini API with model: {MODEL_NAME}")
    print("📍 Access the app at: http://localhost:5000")
    print("💡 Upload a food image to get nutritional analysis\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
