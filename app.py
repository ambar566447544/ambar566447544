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
# 👇 AAPKI NAYI WALI KEY (Jo Telegram me chal rahi hai)
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@app.route("/")
def home():
    return "<h1>Llama 4 Scout Extension is Running! 🚀</h1>"

@app.route("/analyze", methods=["POST"])
def analyze_media():
    print("🔔 Request Received on /analyze", flush=True)
    try:
        data = request.json
        img_url = data.get("image_url")
        
        print(f"📸 Image URL: {img_url}", flush=True)

        if not img_url:
            return jsonify({"description": "Error: No image URL provided."})

        # --- VISION PROCESSING (Llama 4 Scout) ---
        print("🤖 Asking Llama 4 Scout...", flush=True)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Is image ko Hinglish mein describe karo. Batao isme kya kya dikh raha hai detail mein."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_url, # Hum URL bhejenge, Groq isse handle kar lega
                            },
                        },
                    ],
                }
            ],
            # 👇 NAYA MODEL (Jo Telegram me mast chal raha hai)
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.5,
            max_tokens=1024,
        )
        
        description = chat_completion.choices[0].message.content
        print("✅ Analysis Complete!", flush=True)
        return jsonify({"description": description})

    except Exception as e:
        error_msg = f"INTERNAL SERVER ERROR: {str(e)}"
        print(f"🔥 {error_msg}", flush=True)
        return jsonify({"description": error_msg}) # Error ko chat me bhejo

# ================= AUTO-PING (JAGATE RAHO) =================
def keep_alive():
    while True:
        try:
            time.sleep(600)
            requests.get("http://127.0.0.1:10000/")
            print("💓 Auto-Ping sent.")
        except: pass

if __name__ == "__main__":
    Thread(target=keep_alive).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
