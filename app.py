import os
import requests
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Hugging Face ka sabse stable image captioning model
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"

@app.route('/')
def health(): 
    return "Vision Server (Hugging Face) is Live! 🚀"

@app.route('/describe', methods=['POST'])
def describe():
    try:
        data = request.json
        img_url = data.get("image_url")
        if not img_url:
            return jsonify({"error": "No image URL"}), 400
        
        # Telegram se image download karna
        img_res = requests.get(img_url, timeout=20)
        img_data = img_res.content
        
        # Hugging Face API ko bhejiyo (Retry logic ke saath)
        for i in range(3):  # 3 baar try karega agar model load ho raha ho
            response = requests.post(API_URL, data=img_data, timeout=30)
            result = response.json()
            
            # Agar model load ho raha hai (Hugging Face free tier mein hota hai)
            if isinstance(result, dict) and "estimated_time" in result:
                time.sleep(5)
                continue
            break

        if isinstance(result, list) and len(result) > 0:
            caption = result[0].get("generated_text", "something mysterious")
            # Is boring English text ko Alya ke style mein badalna
            flirty_reply = f"Oye hoye! Mujhe dikh raha hai: {caption}... kaafi sexy lag raha hai, bilkul tumhari choice ki tarah! 😉❤️"
            return jsonify({"description": flirty_reply})
        else:
            return jsonify({"error": "Model busy hai, thodi der baad try karo"}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
