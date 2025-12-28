import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from threading import Thread
import PyPDF2
import io
import yt_dlp
import re 

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# 👇 BROWSER JAISA DIKHNE KE LIYE (Bypass Block)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.google.com/'
}

@app.route("/")
def home(): return "<h1>Alya Extension: FIXED & READY 🛠️</h1>"

# 1. IMAGE ANALYSIS
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        url = data.get("image_url")
        if not url: return jsonify({"description": "No URL"}), 400

        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview", # 👈 Vision Model Updated
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "Describe this image in detail in Hinglish."},
                {"type": "image_url", "image_url": {"url": url}}
            ]}],
            temperature=0.3, max_tokens=600
        )
        return jsonify({"description": completion.choices[0].message.content})
    except Exception as e: return jsonify({"description": f"Image Error: {str(e)}"}), 200

# 2. MEDIA & LINKS
@app.route("/process_media", methods=["POST"])
def process_media():
    try:
        data = request.json
        file_url = data.get("file_url") 
        media_type = data.get("media_type")

        # --- A. YOUTUBE LINK (The "Jugaad" Fix) ---
        if media_type == 'link':
            # Method 1: Try yt-dlp (Best Data)
            try:
                ydl_opts = {'quiet': True, 'skip_download': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(file_url, download=False)
                    return jsonify({"result": f"YouTube Video:\nTitle: {info.get('title')}\nDescription: {info.get('description')[:500]}"})
            except:
                # Method 2: HTML Title Scraping (Fail-safe)
                try:
                    r = requests.get(file_url, headers=HEADERS, timeout=10)
                    match = re.search(r'<title>(.*?)</title>', r.text)
                    if match:
                        title = match.group(1).replace("- YouTube", "").strip()
                        return jsonify({"result": f"YouTube Link Title: {title} (Video content hidden due to privacy, judge by title)."})
                except Exception as e:
                    return jsonify({"result": f"Link Error: {str(e)}"})

        # --- B. PDF / DOCUMENTS ---
        if media_type == 'document' or media_type == 'pdf':
            try:
                response = requests.get(file_url, headers=HEADERS)
                f = io.BytesIO(response.content)
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages: text += page.extract_text()
                return jsonify({"result": f"Document Text:\n{text[:4000]}..."})
            except Exception as e: return jsonify({"result": f"PDF Error: {str(e)}"})

        return jsonify({"result": "Unknown Media Type"})

    except Exception as e: return jsonify({"result": f"Server Error: {str(e)}"}), 200

def keep_alive():
    while True:
        try: time.sleep(600); requests.get("http://127.0.0.1:10000/")
        except: pass

if __name__ == "__main__":
    Thread(target=keep_alive).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
