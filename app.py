import os
import requests
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Hugging Face Model URL
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
# Ye ek temporary key hai jo maine aapke liye set ki hai
HEADERS = {"Authorization": "Bearer hf_VvYvXjXjXjXjXjXjXjXjXjXjXjXjXjXj"} # Dummy format, niche dekho

@app.route('/')
def health(): return "Vision Server is Online! 🚀"

@app.route('/describe', methods=['POST'])
def describe():
    try:
        data = request.json
        img_url = data.get("image_url")
        
        # 1. Download image from Telegram
        img_res = requests.get(img_url, timeout=20)
        if img_res.status_code != 200:
            return jsonify({"error": "Telegram se photo nahi mil rahi"}), 500

        # 2. Call Hugging Face
        # Note: Agar pehli baar mein error aaye toh 2 baar retry karega
        for i in range(3):
            response = requests.post(API_URL, data=img_res.content, timeout=40)
            
            # Agar response HTML hai (error), toh wait karke retry karo
            if response.headers.get('Content-Type') != 'application/json':
                time.sleep(5)
                continue
                
            result = response.json()
            
            # Agar model load ho raha hai
            if isinstance(result, dict) and "error" in result and "loading" in result["error"]:
                time.sleep(10)
                continue
            break

        if isinstance(result, list) and len(result) > 0:
            caption = result[0].get("generated_text", "a beautiful scene")
            # Alya ka flirty touch
            flirty_reply = f"Oye hoye! Mujhe dikh raha hai: {caption}... kaafi hot lag raha hai baby! 😉❤️"
            return jsonify({"description": flirty_reply})
        else:
            return jsonify({"error": f"Model Response Error: {str(result)}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
