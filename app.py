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

# HEADERS (Browser Mask)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.google.com/'
}

@app.route("/")
def home(): return "<h1>Alya Extension Hub v5.0 (Bypass Mode) 🛡️</h1>"

# --- IMAGE ---
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        url = data.get("image_url")
        if not url: return jsonify({"description": "No URL"}), 400

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

# --- MEDIA & DOCS ---
@app.route("/process_media", methods=["POST"])
def process_media():
    try:
        data = request.json
        file_url = data.get("file_url") 
        media_type = data.get("media_type")

        if not file_url: return jsonify({"result": "No URL provided"}), 400

        # A. DOCUMENTS
        if media_type == 'document' or media_type == 'pdf':
            try:
                response = requests.get(file_url, headers=HEADERS)
                response.raise_for_status()
                
                # Try Text
                try:
                    text_content = response.content.decode('utf-8')
                    if not text_content.startswith('%PDF'):
                        return jsonify({"result": f"File Content:\n{text_content[:4000]}..."})
                except: pass

                # Try PDF
                f = io.BytesIO(response.content)
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                if not text.strip(): return jsonify({"result": "⚠️ PDF Text Empty (Scanned Doc)."})
                return jsonify({"result": f"Document Content:\n{text[:4500]}..."})
            except Exception as e: return jsonify({"result": f"PDF Error: {str(e)}"})

        # B. AUDIO/VIDEO
        elif media_type in ['audio', 'video']:
            response = requests.get(file_url, headers=HEADERS)
            filename = "temp_media.mp3"
            with open(filename, "wb") as f: f.write(response.content)
            
            with open(filename, "rb") as file_obj:
                transcription = client.audio.transcriptions.create(
                    file=(filename, file_obj.read()),
                    model="whisper-large-v3", language="en"
                )
            return jsonify({"result": f"Audio Transcript: {transcription.text}"})

        # C. LINKS (BYPASS MODE) 🚨
        elif media_type == 'link':
            # Extract Video ID
            video_id = None
            if "youtu.be" in file_url: video_id = file_url.split("/")[-1].split("?")[0]
            elif "v=" in file_url: video_id = file_url.split("v=")[1].split("&")[0]

            # PLAN A: Invidious API (No Block)
            if video_id:
                try:
                    # Using a public instance API
                    api_url = f"https://invidious.jing.rocks/api/v1/videos/{video_id}"
                    resp = requests.get(api_url, timeout=10)
                    if resp.status_code == 200:
                        meta = resp.json()
                        return jsonify({"result": f"Video Info (via API):\nTitle: {meta['title']}\nDescription: {meta['description'][:500]}"})
                except Exception as e: print(f"API Failed: {e}")

            # PLAN B: yt-dlp
            try:
                ydl_opts = {'quiet': True, 'skip_download': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(file_url, download=False)
                    return jsonify({"result": f"Link Info:\nTitle: {info.get('title')}\nDesc: {info.get('description')[:500]}"})
            except: pass
            
            # PLAN C: Basic Request
            try:
                r = requests.get(file_url, headers=HEADERS)
                match = re.search(r'<title>(.*?)</title>', r.text)
                if match: return jsonify({"result": f"Web Page Title: {match.group(1)}"})
            except: pass

            return jsonify({"result": "Link detected but content is strictly protected."})

        return jsonify({"result": "Unknown Media Type"})

    except Exception as e: return jsonify({"result": f"Processing Error: {str(e)}"}), 200

def keep_alive():
    while True:
        try: time.sleep(600); requests.get("http://127.0.0.1:10000/")
        except: pass

if __name__ == "__main__":
    Thread(target=keep_alive).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
