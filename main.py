import base64
from io import BytesIO
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from PIL import Image
from pydantic import BaseModel
import requests
import uvicorn

app = FastAPI(title="AgroVision AI Backend", version="1.0")

# Enable CORS so your React frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],  # Use 3000 instead of 5173 if you're using Create React App
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Root Endpoint
# -------------------------------------------------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to AgroVision AI API"}


# -------------------------------------------------------------------
# Endpoint 1: Static Image Upload (Disease Detection)
# -------------------------------------------------------------------
@app.post("/api/disease-detection")
async def detect_disease(
    file: UploadFile = File(...),
    lang: str = "en"
):

    data = {
        "en": {
            "disease": "Apple Scab",
            "confidence": 0.92,
            "severity": "Medium",
            "medicine": "Copper Oxychloride",
            "recommendation": "Apply copper-based fungicide during dry weather.",
            "prevention": "Remove infected leaves and avoid overhead irrigation.",
            "treatment_days": "Repeat spray after 7 days"
        },

        "hi": {
            "disease": "सेब की पपड़ी",
            "confidence": 0.92,
            "severity": "मध्यम",
            "medicine": "कॉपर ऑक्सीक्लोराइड",
            "recommendation": "सूखे मौसम में कॉपर आधारित फफूंदनाशक का छिड़काव करें।",
            "prevention": "संक्रमित पत्तियाँ हटाएँ और ऊपर से सिंचाई न करें।",
            "treatment_days": "7 दिन बाद दोबारा छिड़काव करें।"
        },

        "bn": {
            "disease": "আপেল স্ক্যাব",
            "confidence": 0.92,
            "severity": "মাঝারি",
            "medicine": "কপার অক্সিক্লোরাইড",
            "recommendation": "শুষ্ক আবহাওয়ায় কপার-ভিত্তিক ছত্রাকনাশক প্রয়োগ করুন।",
            "prevention": "আক্রান্ত পাতা সরিয়ে ফেলুন এবং উপর থেকে পানি দেওয়া এড়িয়ে চলুন।",
            "treatment_days": "৭ দিন পরে আবার স্প্রে করুন।"
        }
    }

    if lang not in data:
        lang = "en"

    return {
        "status": "success",
        **data[lang]
    }

# -------------------------------------------------------------------
# Endpoint 2: Market Advisory
# -------------------------------------------------------------------
@app.get("/api/market-advisory")
def get_market_advisory(crop: str, lang: str = "en"):

    data = {
        "en": {
            "market_trend": "Market price expected to fall by 12%.",
            "recommendation": "Harvest within 48 hours and sell 40% of available stock to prevent losses.",
            "demand": "High",
            "risk_level": "Medium",
            "current_price": 3200,
            "predicted_price": 2820,
            "best_selling_date": "Within 2 days"
        },

        "hi": {
            "market_trend": "बाज़ार मूल्य में लगभग 12% गिरावट आने की संभावना है।",
            "recommendation": "अगले 48 घंटों के भीतर फसल काटें और नुकसान से बचने के लिए उपलब्ध स्टॉक का 40% बेच दें।",
            "demand": "उच्च",
            "risk_level": "मध्यम",
            "current_price": 3200,
            "predicted_price": 2820,
            "best_selling_date": "अगले 2 दिनों के भीतर"
        },

        "bn": {
            "market_trend": "বাজার মূল্য প্রায় ১২% কমতে পারে।",
            "recommendation": "আগামী ৪৮ ঘণ্টার মধ্যে ফসল সংগ্রহ করুন এবং ক্ষতি এড়াতে মোট উৎপাদনের ৪০% বিক্রি করুন।",
            "demand": "উচ্চ",
            "risk_level": "মাঝারি",
            "current_price": 3200,
            "predicted_price": 2820,
            "best_selling_date": "আগামী ২ দিনের মধ্যে"
        }
    }

    if lang not in data:
        lang = "en"

    return {
        "crop": crop.capitalize(),
        **data[lang]
    }


# -------------------------------------------------------------------
# Endpoint 3: Multilingual Farmer AI Chatbot (EN, HI, BN)
# -------------------------------------------------------------------
class ChatMessage(BaseModel):
    message: str
    language: str = "en"  # "en", "hi", or "bn"

@app.post("/api/chatbot")
def farmer_chatbot(chat: ChatMessage):
    msg = chat.message.lower()
    
    # Simple NLP Keyword Matching Engine for Hackathon Demo
    if "disease" in msg or "scab" in msg or "medicine" in msg:
        reply_en = "For Apple Scab or leaf spot, apply a copper-based fungicide during dry weather."
        reply_hi = "सेब की पपड़ी या पत्तों के रोगों के लिए, सूखे मौसम में तांबे-आधारित कवकनाशी (fungicide) लगाएं।"
        reply_bn = "আপেল স্ক্যাব বা পাতার রোগের জন্য, শুষ্ক আবহাওয়ায় তামা-ভিত্তিক ছত্রাকনাশক (fungicide) প্রয়োগ করুন।"
        
    elif "market" in msg or "price" in msg or "sell" in msg:
        reply_en = "Current market trends suggest selling your harvest within 48 hours to avoid a predicted 12% price drop."
        reply_hi = "बाजार के वर्तमान रुझानों से पता चलता है कि 12% की गिरावट से बचने के लिए अगले 48 घंटों के भीतर फसल बेच दें।"
        reply_bn = "বাজারের বর্তমান প্রবণতা অনুযায়ী, ১২% সম্ভাব্য দরপতন এড়াতে আগামী ৪৮ ঘণ্টার মধ্যে ফসল বিক্রি করার পরামর্শ দেওয়া হচ্ছে।"
        
    elif "weather" in msg or "rain" in msg:
        reply_en = "Warning: Heavy rainfall is expected in your region. Delay fertilizer spraying to avoid washing away."
        reply_hi = "चेतावनी: आपके क्षेत्र में भारी बारिश की संभावना है। पानी में बहने से बचाने के लिए उर्वरक का छिड़काव टालें।"
        reply_bn = "সতর্কতা: আপনার এলাকায় ভারী বৃষ্টির সম্ভাবনা রয়েছে। উভে যাওয়া রোধ করতে সার প্রয়োগ পিছিয়ে দিন।"
        
    else:
        reply_en = "Hello! I am your AgroVision AI assistant. Ask me about crop diseases, weather alerts, or market prices."
        reply_hi = "नमस्ते! मैं आपका एग्रोविज़न एआई सहायक हूँ। मुझसे फसल की बीमारियों, मौसम या बाजार भाव के बारे में पूछें।"
        reply_bn = "নমস্কার! আমি আপনার এগ্রোভিশন এআই সহকারী। আমাকে ফসলের রোগ, আবহাওয়া বা বাজারের দাম সম্পর্কে জিজ্ঞাসা করুন।"

    # Return selected language
    if chat.language == "hi":
        return {"reply": reply_hi}
    elif chat.language == "bn":
        return {"reply": reply_bn}
    else:
        return {"reply": reply_en}


# -------------------------------------------------------------------
# Endpoint 4: Smart Decision Engine (Integrated Weather + Market)
# -------------------------------------------------------------------
# Replace with your actual key from openweathermap.org if available
OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"

@app.get("/api/smart-decision")
def get_smart_decision(crop: str, city: str = "Contai"):
    weather_alert = "Weather data based on regional forecast."
    
    # Try fetching real OpenWeatherMap API data
    if OPENWEATHER_API_KEY != "YOUR_API_KEY_HERE":
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                weather_data = response.json()
                condition = weather_data['weather'][0]['main']
                temp = weather_data['main']['temp']
                weather_alert = f"Current conditions in {city}: {condition}, {temp}°C."
                if condition.lower() in ["rain", "thunderstorm", "drizzle"]:
                    weather_alert += " ⚠️ Rain expected. Hold chemical spraying."
        except Exception:
            weather_alert = "Weather service temporarily unavailable."

    # Dynamic recommendation structure based on crop
    if crop.lower() == "mango":
        return {
            "crop": "Mango",
            "weather_alert": weather_alert if OPENWEATHER_API_KEY != "YOUR_API_KEY_HERE" else "Heavy rain expected in 3 days.",
            "maturity_level": "85%",
            "market_trend": "Market price expected to fall by 12%.",
            "ai_recommendation": "Harvest within 48 hours and sell 40% of available stock to prevent losses."
        }
    else:
        return {
            "crop": crop.capitalize(),
            "weather_alert": weather_alert,
            "maturity_level": "60%",
            "market_trend": "Market prices are stable.",
            "ai_recommendation": "Continue standard irrigation and monitoring. Not ready for harvest yet."
        }


# -------------------------------------------------------------------
# Live Camera Scanner API
# -------------------------------------------------------------------
import random
import base64
from io import BytesIO
import numpy as np
from PIL import Image
from pydantic import BaseModel

class ImageData(BaseModel):
    image_base64: str

@app.post("/api/live-scan")
def live_scan(data: ImageData):
    try:
        print("=" * 50)
        print("Live Scan Request Received")

        # Check Base64 size
        print("Base64 Length:", len(data.image_base64))

        image_bytes = base64.b64decode(data.image_base64)

        print("Image Bytes:", len(image_bytes))

        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        print("Image Size:", image.size)

        np_image = np.array(image)

        avg_red = np.mean(np_image[:, :, 0])
        avg_green = np.mean(np_image[:, :, 1])
        avg_blue = np.mean(np_image[:, :, 2])

        print("RGB:", avg_red, avg_green, avg_blue)

        confidence = round(random.uniform(0.88, 0.99), 2)

        if avg_green > 120:
            result = {
                "plant_name": "Healthy Green Plant",
                "type": "Vegetable",
                "disease": "None Detected",
                "confidence": confidence,
                "severity": "None",
                "medicine": "No medicine required.",
                "prevention": "Continue regular watering.",
                "weather_alert": "Weather is suitable.",
                "maturity_level": "85%",
                "harvest_ready": True
            }

        elif avg_red > avg_green + 20:
            result = {
                "plant_name": "Ripening Fruit",
                "type": "Fruit",
                "disease": "None",
                "confidence": confidence,
                "severity": "None",
                "medicine": "No treatment required.",
                "prevention": "Protect fruits from insects.",
                "weather_alert": "Dry weather is suitable.",
                "maturity_level": "95%",
                "harvest_ready": True
            }

        else:
            result = {
                "plant_name": "Leaf Sample",
                "type": "Plant",
                "disease": "Early Blight",
                "confidence": confidence,
                "severity": "High",
                "medicine": "Copper Oxychloride",
                "prevention": "Remove infected leaves.",
                "weather_alert": "High humidity detected.",
                "maturity_level": "45%",
                "harvest_ready": False
            }

        print(result)

        return result

    except Exception as e:
        print("ERROR:", e)
        return {
            "success": False,
            "error": str(e)
        }
    
# # -------------------------------------------------------------------
# # Real Time Weather API
# # -------------------------------------------------------------------

# OPENWEATHER_API_KEY = " 4002796"


# @app.get("/api/weather")
# def get_weather(city: str = "Contai"):

#     try:

#         url = (
#             "https://api.openweathermap.org/data/2.5/weather"
#             f"?q={city}"
#             f"&appid={OPENWEATHER_API_KEY}"
#             "&units=metric"
#         )


#         response = requests.get(
#             url,
#             timeout=10
#         )


#         data = response.json()


#         if response.status_code != 200:
#             return {
#                 "error": "Weather data not available"
#             }


#         return {

#             "place": data["name"],

#             "country":
#             data["sys"]["country"],


#             "temperature":
#             data["main"]["temp"],


#             "feels_like":
#             data["main"]["feels_like"],


#             "humidity":
#             data["main"]["humidity"],


#             "wind":
#             data["wind"]["speed"],


#             "pressure":
#             data["main"]["pressure"],


#             "rain":
#             data.get("rain", {})
#                 .get("1h", 0),


#             "condition":
#             data["weather"][0]["description"],


#             "icon":
#             data["weather"][0]["icon"]

#         }


#     except Exception as e:

#         return {
#             "error": str(e)
#         }


# -------------------------------------------------------------------
# Server Execution Block
# -------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)