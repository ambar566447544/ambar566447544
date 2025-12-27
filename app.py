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

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@app.route("/")
def home(): return "<h1>Alya Extension Hub v2.0 (Smart Docs) 🛠️</h1>"

# --- 1. IMAGE ---
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

# --- 2. DOCS & MEDIA ---
@app.route("/process_media", methods=["POST"])
def process_media():
    try:
        data = request.json
        file_url = data.get("file_url") 
        media_type = data.get("media_type")

        if not file_url: return jsonify({"result": "No URL provided"}), 400

        # A. DOCUMENTS (Text/PDF)
        if media_type == 'pdf' or media_type == 'document':
            try:
                response = requests.get(file_url)
                response.raise_for_status()
                
                # 1. Try as Text first
                try:
                    text_content = response.content.decode('utf-8')
                    if not text_content.startswith('%PDF'):
                        return jsonify({"result": f"File Content:\n{text_content[:4000]}..."})
                except: pass

                # 2. Try as PDF
                f = io.BytesIO(response.content)
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted: text += extracted + "\n"
                
                if not text.strip():
                    return jsonify({"result": "⚠️ PDF Khali laga. Sayad ye Scanned Image hai."})
                
                return jsonify({"result": f"Document Content:\n{text[:4000]}..."})
            except Exception as e:
                return jsonify({"result": f"Doc Read Error: {str(e)}"})

        # B. AUDIO/VIDEO
        elif media_type in ['audio', 'video']:
            response = requests.get(file_url)
            filename = "temp_media.mp3"
            with open(filename, "wb") as f: f.write(response.content)
            
            with open(filename, "rb") as file_obj:
                transcription = client.audio.transcriptions.create(
                    file=(filename, file_obj.read()),
                    model="whisper-large-v3",
                    language="en"
                )
            return jsonify({"result": f"Audio Transcript: {transcription.text}"})

        # C. LINKS
        elif media_type == 'link':
            ydl_opts = {'quiet': True, 'skip_download': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(file_url, download=False)
                return jsonify({"result": f"Link Info:\nTitle: {info.get('title')}\nDesc: {info.get('description')[:500]}"})

        return jsonify({"result": "Unknown Media Type"})

    except Exception as e:
        return jsonify({"result": f"Processing Error: {str(e)}"}), 200

def keep_alive():
    while True:
        try: time.sleep(600); requests.get("http://127.0.0.1:10000/")
        except: pass

if __name__ == "__main__":
    Thread(target=keep_alive).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
