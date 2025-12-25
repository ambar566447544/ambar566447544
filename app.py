import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import threading
import time
import requests

app = Flask(__name__)
CORS(app)

# 👇 Aapki API Key
client = Groq(api_key="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")

@app.route("/")
def home():
    return "<h1>Vision Server (Scout Model) Online 🟢</h1>"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        img_url = data.get("image_url")
        if not img_url: return jsonify({"description": "No Image Found"}), 400

        print(f"Analyzing image with Scout model: {img_url}")

        # 👇 WAPAS WAHI PURANA "SCOUT" MODEL
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", 
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail in Hinglish."},
                    {"type": "image_url", "image_url": {"url": img_url}}
                ]
            }],
            temperature=0.3, # Thoda kam temperature taaki fast ho
            max_tokens=500
        )
        return jsonify({"description": completion.choices[0].message.content})

    except Exception as e:
        print(f"Vision Error: {e}")
        return jsonify({"description": f"Model Error: {str(e)}"}), 200

def keep_alive():
    while True:
        try:
            time.sleep(600)
            requests.get("http://127.0.0.1:10000/")
        except: pass

if __name__ == "__main__":
    threading.Thread(target=keep_alive).start()
    app.run(host="0.0.0.0", port=10000)
