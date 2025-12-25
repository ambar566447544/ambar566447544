import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from threading import Thread

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# Extension Server ki API Key
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@app.route("/")
def home():
    return "<h1>Alya Extension (Vision) is Awake & Running! 👁️</h1>"

@app.route("/analyze", methods=["POST"])
def analyze_media():
    try:
        data = request.json
        img_url = data.get("image_url")
        
        # Future me agar PDF text bhejna ho to yahan receive kar sakte ho
        # doc_text = data.get("doc_text") 

        print(f"Extension received image: {img_url}")

        if not img_url:
            return jsonify({"description": "No image provided."})

        # --- VISION PROCESSING (Sirf yahan hogi) ---
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-instant",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail mainly focusing on visual elements, text, and context so the main AI can chat about it."},
                    {"type": "image_url", "image_url": {"url": img_url}}
                ]
            }]
        )
        
        description = completion.choices[0].message.content
        return jsonify({"description": description})

    except Exception as e:
        print(f"Extension Error: {e}")
        return jsonify({"error": str(e)}), 500

# ================= AUTO-WAKEUP SYSTEM =================
def keep_alive():
    while True:
        try:
            time.sleep(600) # Har 10 minute mein
            # Khud ko ping karke jagaye rakhega
            requests.get("http://127.0.0.1:10000/")
            print("Auto-Ping sent to keep Extension awake.")
        except Exception as e:
            print(f"Auto-Ping failed: {e}")

if __name__ == "__main__":
    # Background thread start
    t = Thread(target=keep_alive)
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
