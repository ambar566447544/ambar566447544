import os
import requests
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from threading import Thread
import time

app = Flask(__name__)
CORS(app)

# 👇 API Key Debug Check
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@app.route("/")
def home():
    return "<h1>Alya Vision Server is Online! 👁️</h1>"

@app.route("/analyze", methods=["POST"])
def analyze_media():
    # Force logs to appear immediately (flush=True)
    print("🔔 Request Received on /analyze", flush=True) 
    
    try:
        data = request.json
        # Agar data None hai (Main server ne JSON nahi bheja)
        if not data:
            print("❌ No JSON data received", flush=True)
            return jsonify({"description": "Error: No data received from Main Server."})

        img_url = data.get("image_url")
        print(f"📸 Image URL: {img_url}", flush=True)

        if not img_url:
            return jsonify({"description": "Error: Image URL missing."})

        # --- VISION PROCESSING ---
        print("🤖 Sending to Groq...", flush=True)
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-instant",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image briefly."},
                    {"type": "image_url", "image_url": {"url": img_url}}
                ]
            }]
        )
        
        description = completion.choices[0].message.content
        print("✅ Success!", flush=True)
        return jsonify({"description": description})

    except Exception as e:
        # 👇 CRITICAL FIX: Agar error aaye to CRASH mat ho, Error wapas bhejo
        error_msg = f"INTERNAL SERVER ERROR: {str(e)}"
        print(f"🔥 {error_msg}", flush=True)
        # Hum 200 OK bhejenge taaki Main Server is error ko User ko dikha sake
        return jsonify({"description": error_msg})

# Keep Alive
def keep_alive():
    while True:
        try:
            time.sleep(600)
            requests.get("http://127.0.0.1:10000/")
        except: pass

if __name__ == "__main__":
    Thread(target=keep_alive).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
