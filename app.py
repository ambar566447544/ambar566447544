import os
import base64
import telebot
from groq import Groq
from flask import Flask
from threading import Thread

# --- 1. CONFIGURATION ---
# Render ke "Environment Variables" se keys aayengi
TELEGRAM_TOKEN = os.environ.get("8431298254:AAEoEW2sflJrvPwR2bnzkI6h0f2p7vJFogg")
GROQ_API_KEY = os.environ.get("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")

# Groq Client
client = Groq(api_key=GROQ_API_KEY)

# Telegram Bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Flask Server (Render ko 24/7 chalane ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running! Llama-4 Scout Active 🚀"

def run_http_server():
    app.run(host='0.0.0.0', port=10000)

# --- 2. IMAGE ENCODER (Groq ko Base64 chahiye) ---
def encode_image(image_data):
    return base64.b64encode(image_data).decode('utf-8')

# --- 3. BOT LOGIC ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Namaste! 📸 Photo bhejo, main 'Llama 4 Scout' se dekh kar bataunga.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # User ko batao hum kaam kar rahe hain
        sent_msg = bot.reply_to(message, "Image analyze ho rahi hai... ⚡")

        # A. Telegram se photo uthao
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # B. Photo ko Base64 mein badlo
        base64_image = encode_image(downloaded_file)

        # C. Groq API Call (Aapka wala Model)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Is image ko Hinglish mein detail mein describe karo. Batao kya kya dikh raha hai."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            # YAHAN HAI WO MODEL JO AAPNE SCREENSHOT MEIN DIKHAYA 👇
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.5,
            max_tokens=1024,
        )

        # D. Jawab User ko bhejo
        reply_text = chat_completion.choices[0].message.content
        bot.edit_message_text(reply_text, chat_id=message.chat.id, message_id=sent_msg.message_id)

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        bot.reply_to(message, "Bhai, Groq ka server busy hai ya key expire ho gayi hai.")

# --- 4. MAIN EXECUTION ---
if __name__ == "__main__":
    t = Thread(target=run_http_server)
    t.start()
    bot.infinity_polling()
