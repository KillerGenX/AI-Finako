import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from backend.core.config import settings
from backend.core.bot_auth import authenticate_telegram_user
from backend.services.scout_service import discover_account
from backend.models.scout_models import OpportunityUpdate

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    telegram_id = user.id
    
    # Authenticate
    client = authenticate_telegram_user(telegram_id)
    if not client:
        await update.message.reply_text(
            f"⛔ Maaf, Telegram ID Anda ({telegram_id}) tidak terdaftar di sistem Finako AI.\n"
            "Silakan daftarkan ID Anda ke tabel 'profiles' di Supabase."
        )
        return
        
    await update.message.reply_text(
        f"Halo {user.first_name}! 🚀 Saya Scout AI dari Finako.\n"
        "Silakan ketikkan pencarian perusahaan yang ingin Anda analisis.\n"
        "Contoh: 'Cari perusahaan kelapa sawit di Riau'"
    )

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming search queries."""
    telegram_id = update.effective_user.id
    query = update.message.text
    
    # Authenticate
    client = authenticate_telegram_user(telegram_id)
    if not client:
        await update.message.reply_text("⛔ Akses ditolak. Telegram ID tidak terdaftar.")
        return
        
    # Inform user that the process has started
    status_msg = await update.message.reply_text("🔍 Memulai riset perusahaan... (Ini butuh waktu beberapa detik)")
    
    try:
        # Run discover_account
        user_id = client.finako_user_id
        opportunities = await discover_account(query, user_id, client)
        
        if not opportunities:
            await status_msg.edit_text("⚠️ Tidak ada perusahaan yang berhasil dianalisis atau memenuhi kriteria.")
            return
            
        await status_msg.edit_text(f"✅ Riset selesai! Menemukan {len(opportunities)} perusahaan yang relevan.")
        
        # Send each opportunity with inline buttons
        for item in opportunities:
            opp_id = item["opportunity"]["id"]
            analysis = item["analysis"]
            
            text = (
                f"🏢 *{analysis.company_name}*\n"
                f"Skor: {analysis.evaluation.score}/100\n"
                f"Alasan: {analysis.evaluation.reasoning}\n"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("Approve", callback_data=f"approve_{opp_id}"),
                    InlineKeyboardButton("Reject", callback_data=f"reject_{opp_id}"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Error during scout discovery: {e}")
        await status_msg.edit_text("❌ Terjadi kesalahan internal saat melakukan pencarian.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the opportunity status."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    client = authenticate_telegram_user(telegram_id)
    
    if not client:
        await query.edit_message_text(text="⛔ Akses ditolak.")
        return
        
    data = query.data
    action, opp_id = data.split("_")
    
    new_status = "evaluating" if action == "approve" else "rejected"
    
    # Update status in database using the authenticated client
    try:
        response = client.table("opportunities").update({"status": new_status}).eq("id", opp_id).execute()
        if not response.data:
            await query.edit_message_text(text="❌ Peluang tidak ditemukan atau Anda tidak memiliki akses.")
            return
            
        # Update the message text to remove the buttons and show the new status
        original_text = query.message.text
        await query.edit_message_text(text=f"{original_text}\n\n👉 *Status:* {new_status.upper()}", parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        await query.edit_message_text(text="❌ Gagal mengupdate status di database.")

def create_bot_app() -> Application:
    """Create and return the Telegram Bot Application."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is not set. Bot will not start.")
        return None
        
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    return application
