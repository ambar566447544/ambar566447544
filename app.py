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

# 👇 STRONG HEADERS (Mask)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

@app.route("/")
def home(): return "<h1>Extension Hub v5.0 (YouTube Bypass)</h1>"

# --- MEDIA PROCESSOR ---
@app.route("/process_media", methods=["POST"])
def process_media():
    try:
        data = request.json
        file_url = data.get("file_url") 
        media_type = data.get("media_type")

        if not file_url: return jsonify({"result": "No URL provided"}), 400

        # --- YOUTUBE LINK BYPASS (Invidious API) ---
        if media_type == 'link':
            # 1. Video ID Nikalo
            video_id = None
            if "youtu.be" in file_url: video_id = file_url.split("/")[-1].split("?")[0]
            elif "v=" in file_url: video_id = file_url.split("v=")[1].split("&")[0]

            if video_id:
                try:
                    # Invidious API (No Block)
                    api_url = f"https://invidious.jing.rocks/api/v1/videos/{video_id}"
                    resp = requests.get(api_url, timeout=10)
                    if resp.status_code == 200:
                        meta = resp.json()
                        return jsonify({"result": f"YouTube Video Info:\nTitle: {meta['title']}\nDescription: {meta['description'][:600]}..."})
                except Exception as e:
                    print(f"API Fail: {e}")

            # Fallback to HTML Scraping
            try:
                r = requests.get(file_url, headers=HEADERS)
                match = re.search(r'<title>(.*?)</title>', r.text)
                if match: 
                    return jsonify({"result": f"Web Page Title: {match.group(1)}"})
            except: pass
            
            return jsonify({"result": "Link detected but secure."})

        # --- PDF/DOCS ---
        if media_type == 'document' or media_type == 'pdf':
            try:
                response = requests.get(file_url, headers=HEADERS) # Mask lagaya
                f = io.BytesIO(response.content)
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages: text += page.extract_text()
                if not text.strip(): return jsonify({"result": "PDF Empty (Scanned Image)."})
                return jsonify({"result": f"PDF Content: {text[:4000]}"})
            except Exception as e: return jsonify({"result": f"PDF Error: {str(e)}"})
            
        return jsonify({"result": "Unknown Media Type"})

    except Exception as e: return jsonify({"result": f"Error: {str(e)}"}), 200

# --- IMAGE (UNCHANGED) ---
@app.route("/analyze", methods=["POST"])
def analyze():
    # ... (Keep your old Image code here) ...
    # Agar code nahi hai to batao, mai de dunga.
    return jsonify({"description": "Image analysis ready"})

def keep_alive():
    while True:
        try: time.sleep(600); requests.get("http://127.0.0.1:10000/")
        except: pass

if __name__ == "__main__":
    Thread(target=keep_alive).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
