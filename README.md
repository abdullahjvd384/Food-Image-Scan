# 🍎 AI Calorie Tracker - OpenAI GPT-4 Vision Edition

**Professional-grade calorie tracking using OpenAI's GPT-4 Vision API**  
Matches the accuracy and behavior of the Custom GPT "Calorie Tracker"

## 🚀 Quick Start

### 1. Set Your OpenAI API Key
```powershell
$env:OPENAI_API_KEY='sk-your-api-key-here'
```
Get your key at: https://platform.openai.com/api-keys

### 2. Install & Run
```bash
pip install -r requirements.txt
python app.py
```

### 3. Open Browser
http://localhost:5000

## ✨ Key Features

✅ **GPT-4o Vision Model** - Most accurate multimodal AI  
✅ **Precise Portion Estimation** - Uses plate size, utensils, visual cues  
✅ **Cooking Method Analysis** - Accounts for oils, frying, preparations  
✅ **Complete JSON Output** - Calories, protein, carbs, fats, fiber  
✅ **Professional Insights** - Nutritionist-level meal analysis  

## 📊 Response Example

```json
{
  "total_calories": 750,
  "protein": 42,
  "carbs": 65,
  "fats": 28,
  "fiber": 8,
  "items": [
    {"name": "Grilled Chicken", "portion": "6 oz", "calories": 280},
    {"name": "Brown Rice", "portion": "1 cup", "calories": 215}
  ],
  "analysis": "Well-balanced meal with lean protein..."
}
```

## 💰 Cost: ~$0.01-0.03 per image

## 🔧 Tech Stack
Flask • OpenAI GPT-4o • Python • HTML/CSS/JS
