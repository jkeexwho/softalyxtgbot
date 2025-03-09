from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from config import BOT_TOKEN, ADMIN_CHAT_ID
from states import ConversationState
import logging
import json

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation and ask for name."""
    welcome_message = (
        "👋 Hello! I'm the Softalyx's assistant bot.\n\n"
        "I'll help you submit your request. First, could you please tell me your name?"
    )
    await update.message.reply_text(welcome_message)
    return ConversationState.NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store name and ask for email."""
    user_name = update.message.text
    context.user_data['name'] = user_name
    
    await update.message.reply_text(
        f"Nice to meet you, {user_name}! Could you please share your email address or any other contact information?"
    )
    return ConversationState.EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store contact info and ask for contact preference."""
    contact_info = update.message.text
    context.user_data['email'] = contact_info
    
    reply_keyboard = [[
        'Telegram',
        'Email'
    ]]
    await update.message.reply_text(
        "What is your preferred method of contact?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    return ConversationState.CONTACT_PREFERENCE

async def get_contact_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store contact preference and ask for the request details."""
    preference = update.message.text
    if preference not in ['Telegram', 'Email']:
        await update.message.reply_text(
            "Please select either Telegram or Email using the buttons below.",
            reply_markup=ReplyKeyboardMarkup(
                [['Telegram', 'Email']],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return ConversationState.CONTACT_PREFERENCE
    
    context.user_data['contact_preference'] = preference
    
    await update.message.reply_text(
        "Please describe your request or question in detail:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationState.REQUEST

async def get_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store request and ask for privacy policy acceptance."""
    request_text = update.message.text
    context.user_data['request'] = request_text
    
    reply_keyboard = [[
        'I Accept',
        'I Decline'
    ]]
    await update.message.reply_text(
        "To process your request, we need your consent to handle your personal data.\n\n"
        "By accepting, you agree that we can process your personal information "
        "to handle your request and contact you back.\n\n"
        "Do you accept our privacy policy?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    return ConversationState.PRIVACY_POLICY

async def handle_privacy_policy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Final step - handle privacy policy response and forward to admin if accepted."""
    response = update.message.text
    user = update.message.from_user
    
    if response != 'I Accept':
        await update.message.reply_text(
            "We cannot process your request without your consent. "
            "You can start a new request anytime with /start",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    # Format collected information
    admin_message = (
        f"📨 New Request:\n\n"
        f"👤 Name: {context.user_data['name']}\n"
        f"📧 Contact Info: {context.user_data['email']}\n"
        f"📱 Preferred Contact: {context.user_data['contact_preference']}\n"
        f"🆔 Telegram: @{user.username if user.username else 'Not provided'}\n\n"
        f"📝 Request:\n{context.user_data['request']}\n\n"
        f"✅ Privacy Policy: Accepted"
    )
    
    # Send to admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_message
    )
    
    # Send confirmation to user
    await update.message.reply_text(
        "Thank you for your request! We have received it and will contact you soon "
        f"via your preferred method ({context.user_data['contact_preference']}).",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await update.message.reply_text(
        "Conversation cancelled. You can start a new request anytime with /start",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def handle_website_request(request_data: dict) -> bool:
    """Handle requests coming from the website."""
    try:
        bot = Application.builder().token(BOT_TOKEN).build()
        
        # Format website request
        website_request = (
            f"🌐 Website Request:\n\n"
            f"👤 Name: {request_data.get('name', 'Not provided')}\n"
            f"📧 Contact Info: {request_data.get('email', 'Not provided')}\n"
            f"📱 Preferred Contact: {request_data.get('contact_preference', 'Not provided')}\n"
            f"📝 Request:\n{request_data.get('message', 'Not provided')}\n\n"
            f"✅ Privacy Policy: {request_data.get('privacy_accepted', 'Not provided')}"
        )
        
        # Send to admin
        async with bot:
            await bot.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=website_request
            )
        return True
    except Exception as e:
        logger.error(f"Error handling website request: {e}")
        return False

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ConversationState.NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)
            ],
            ConversationState.EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)
            ],
            ConversationState.CONTACT_PREFERENCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact_preference)
            ],
            ConversationState.REQUEST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_request)
            ],
            ConversationState.PRIVACY_POLICY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_privacy_policy)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 