import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator

load_dotenv()

# Store user language preferences in memory (for simplicity)
user_languages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_text = (
        "👋 Welcome! I am a translator bot.\n\n"
        "Simply send me a message, and I'll translate it. "
        "By default, I translate to English.\n\n"
        "Use /lang to change the target language."
    )
    await update.message.reply_text(welcome_text)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide buttons to change the target language."""
    keyboard = [
        [InlineKeyboardButton("Spanish 🇪🇸", callback_data='es')],
        [InlineKeyboardButton("French 🇫🇷", callback_data='fr')],
        [InlineKeyboardButton("German 🇩🇪", callback_data='de')],
        [InlineKeyboardButton("English 🇬🇧", callback_data='en')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose a target language:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection buttons."""
    query = update.callback_query
    await query.answer()
    lang_code = query.data
    user_id = update.effective_user.id
    user_languages[user_id] = lang_code
    await query.edit_message_text(text=f"Target language set to: {lang_code.upper()}")

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate any text message sent by the user."""
    user_id = update.effective_user.id
    target_lang = user_languages.get(user_id, 'en') # Default to English
    
    text_to_translate = update.message.text
    
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text_to_translate)
        await update.message.reply_text(translated)
    except Exception as e:
        await update.message.reply_text("Sorry, I couldn't translate that. Please try again.")

def main():
    """Start the bot."""
    # Use the token from environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables.")

    application = Application.builder().token(token).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("lang", set_language))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))
    application.add_handler(MessageHandler(filters.StatusUpdate.ALL, button)) # For buttons

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
