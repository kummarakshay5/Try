import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from geopy.geocoders import Nominatim

# --- YE DUMMY SERVER HAI KOYEB KO KHUSH RAKHNE KE LIYE ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    # Koyeb default port 8000 use karta hai
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- BOT KA ASLI LOGIC ---
TOKEN = os.getenv("BOT_TOKEN")
geolocator = Nominatim(user_agent="my_geo_bot_v2")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (f"Namaste {user.first_name}!\n🆔 ID: `{user.id}`\n"
                    "📍 Location button par click karein:")
    keyboard = [[KeyboardButton("📍 Share Location", request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    try:
        address = geolocator.reverse(f"{loc.latitude}, {loc.longitude}", timeout=10).raw.get('address', {})
        result = (f"🌍 Country: {address.get('country', 'N/A')}\n"
                  f"🏙️ State: {address.get('state', 'N/A')}\n"
                  f"🏙️ City: {address.get('city') or address.get('town', 'N/A')}")
    except:
        result = f"Lat: {loc.latitude}, Lon: {loc.longitude}"
    await update.message.reply_text(result)

if __name__ == '__main__':
    # Dummy server ko background thread mein start karein
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # Bot start karein
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    print("Bot is running...")
    app.run_polling()
