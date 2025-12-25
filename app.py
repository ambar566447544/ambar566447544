import os, time, requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from threading import Thread

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@app.route("/")
def home(): return "<h1>Vision Server (Llama-4 Scout) Online 👁️</h1>"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        url = data.get("image_url")
        if not url: return jsonify({"description": "No URL"}), 400

        # 👇 Optimized for Fast Response
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "Hinglish me describe karo is photo ko."},
                {"type": "image_url", "image_url": {"url": url}}
            ]}],
            temperature=0.3, max_tokens=600
        )
        return jsonify({"description": completion.choices[0].message.content})
    except Exception as e: return jsonify({"description": f"Vision Error: {str(e)}"}), 200

def keep_alive():
    while True:
        try: time.sleep(600); requests.get("http://127.0.0.1:10000/")
        except: pass

if __name__ == "__main__":
    Thread(target=keep_alive).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
