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

# --- CONFIGURATIONS ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@app.route("/")
def home(): return "<h1>Alya Extension Hub (Vision + Media + Docs) 🛠️</h1>"

# ================= 1. IMAGE SYSTEM (UNCHANGED) =================
# Bhai, isko maine bilkul nahi cheda hai, ye waisa hi hai
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

# ================= 2. NEW: UNIVERSAL MEDIA PROCESSOR =================
# Ye route: PDF, Audio, Video, aur Links (Insta/YouTube) sab sambhalega
@app.route("/process_media", methods=["POST"])
def process_media():
    try:
        data = request.json
        file_url = data.get("file_url") # Cloudinary URL or YouTube Link
        media_type = data.get("media_type") # 'pdf', 'audio', 'video', 'link'

        if not file_url: return jsonify({"result": "No URL provided"}), 400

        # --- A. PDF / DOCUMENT ---
        if media_type == 'pdf':
            response = requests.get(file_url)
            f = io.BytesIO(response.content)
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return jsonify({"result": f"Document Content:\n{text[:4000]}..."}) # Limit text

        # --- B. AUDIO / VIDEO FILES (From Cloudinary) ---
        elif media_type in ['audio', 'video']:
            # Video/Audio ko download karke Groq Whisper se sunenge
            # Note: Groq file mangta hai, URL nahi. Isliye download zaroori hai.
            response = requests.get(file_url)
            filename = "temp_media.mp3" # Video ko bhi audio ki tarah treat karenge
            with open(filename, "wb") as f:
                f.write(response.content)
            
            with open(filename, "rb") as file_obj:
                transcription = client.audio.transcriptions.create(
                    file=(filename, file_obj.read()),
                    model="whisper-large-v3",
                    language="en" # Hinglish support
                )
            return jsonify({"result": f"Audio/Video Transcript: {transcription.text}"})

        # --- C. YOUTUBE / INSTAGRAM LINKS ---
        elif media_type == 'link':
            # yt-dlp se title aur info nikalenge (Video download heavy padega)
            ydl_opts = {'quiet': True, 'skip_download': True} # Sirf Info chahiye
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(file_url, download=False)
                title = info.get('title', 'Unknown')
                desc = info.get('description', 'No description')
                return jsonify({"result": f"Link Info:\nTitle: {title}\nDescription: {desc[:500]}"})

        return jsonify({"result": "Unknown Media Type"})

    except Exception as e:
        return jsonify({"result": f"Processing Error: {str(e)}"}), 200

# ================= AUTO-PING =================
def keep_alive():
    while True:
        try: time.sleep(600); requests.get("http://127.0.0.1:10000/")
        except: pass

if __name__ == "__main__":
    Thread(target=keep_alive).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
