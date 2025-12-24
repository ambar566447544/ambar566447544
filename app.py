import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

app = Flask(__name__)

# Gemini Key
genai.configure(api_key="AIzaSyDzD50kdDI2YN0XIBk7Tbpc74mMHauJ7CM")

# Yahan 'gemini-1.5-flash-latest' use kar rahe hain jo 404 nahi dega
model = genai.GenerativeModel('gemini-1.5-flash-latest')

@app.route('/')
def health(): return "Vision Server is Running! 👀"

@app.route('/describe', methods=['POST'])
def describe():
    try:
        data = request.json
        img_url = data.get("image_url")
        if not img_url:
            return jsonify({"error": "No image URL"}), 400
        
        img_res = requests.get(img_url, timeout=20)
        image_parts = [{"mime_type": "image/jpeg", "data": img_res.content}]
        
        prompt = "Tum Alya ho. Is photo ko dekh kar ek flirty Hinglish comment karo. Short aur spicy."
        response = model.generate_content([prompt, image_parts[0]])
        
        return jsonify({"description": response.text})
    except Exception as e:
        return jsonify({"error": f"Gemini Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
