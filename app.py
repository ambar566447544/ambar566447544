import os
import base64
import telebot
from groq import Groq
from flask import Flask
from threading import Thread

# --- 1. CONFIGURATION (Direct Keys) ---
# Maine aapki keys yahan seedhi likh di hain
TELEGRAM_TOKEN = "8431298254:AAEoEW2sflJrvPwR2bnzkI6h0f2p7vJFogg"
GROQ_API_KEY = "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"

# Groq Client Setup
client = Groq(api_key=GROQ_API_KEY)

# Telegram Bot Setup
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Flask Server (Render ko 24/7 zinda rakhne ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running! Llama-4 Scout Active 🚀"

def run_http_server():
    # Render port 10000 use karta hai
    app.run(host='0.0.0.0', port=10000)

# --- 2. IMAGE ENCODER ---
def encode_image(image_data):
    return base64.b64encode(image_data).decode('utf-8')

# --- 3. BOT LOGIC ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Namaste! 📸 Photo bhejo, main 'Llama 4 Scout' model se dekh kar bataunga kya hai.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # User ko batao hum kaam kar rahe hain
        sent_msg = bot.reply_to(message, "Ruko, Llama-4 se dekh raha hu... ⚡")

        # A. Telegram se photo download karo
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # B. Photo ko Base64 mein badlo (Groq ke liye)
        base64_image = encode_image(downloaded_file)

        # C. Groq API Call (Llama 4 Scout Model)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Is image ko Hinglish mein describe karo. Batao isme kya kya dikh raha hai detail mein."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            # Aapka pasandida model
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
        bot.reply_to(message, "Sorry bhai, Groq server busy hai ya model load nahi hua.")

# --- 4. MAIN EXECUTION ---
if __name__ == "__main__":
    # Flask thread start
    t = Thread(target=run_http_server)
    t.start()
    
    # Bot start
    print("Bot chalu ho gaya hai...")
    bot.infinity_polling()
