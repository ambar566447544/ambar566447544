import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from threading import Thread
import time

app = Flask(__name__)
CORS(app)

# ================= CONFIGURATION =================
# 👇 Aapki Key (Maine Hardcode kar di taaki error na aaye)
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@app.route("/")
def home():
    return "<h1>Alya Extension (Vision) is Awake & Running! 👁️</h1>"

@app.route("/analyze", methods=["POST"])
def analyze_media():
    print("🔔 Request Received on /analyze") # Logs me dikhega
    try:
        data = request.json
        img_url = data.get("image_url")
        print(f"📸 Image URL received: {img_url}")

        if not img_url:
            return jsonify({"description": "No image provided."})

        # --- VISION PROCESSING ---
        print("🤖 Asking Groq Vision AI...")
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-instant",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail mainly focusing on visual elements."},
                    {"type": "image_url", "image_url": {"url": img_url}}
                ]
            }]
        )
        
        description = completion.choices[0].message.content
        print("✅ Analysis Complete!")
        return jsonify({"description": description})

    except Exception as e:
        # 👇 YE LINE AAPKO BATAYEGI KI GALTI KYA HAI LOGS MEIN
        print(f"🔥 CRITICAL ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================= AUTO-WAKEUP SYSTEM =================
def keep_alive():
    while True:
        try:
            time.sleep(600)
            # Khud ko ping karega port 10000 par
            requests.get("http://127.0.0.1:10000/")
            print("💓 Auto-Ping sent.")
        except:
            pass

if __name__ == "__main__":
    t = Thread(target=keep_alive)
    t.start()
    
    # Render Port handle karega
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
