import logging
from telegram.ext import Application, ApplicationBuilder
from app.config import get_settings
from app.telegram.handlers import setup_handlers

settings = get_settings()
logger = logging.getLogger(__name__)

_application: Application | None = None


def create_bot() -> Application:
    """Create and configure the Telegram bot application."""
    global _application
    
    if _application is not None:
        return _application
    
    logger.info("Creating Telegram bot application...")
    
    _application = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )
    
    # Setup handlers
    setup_handlers(_application)
    
    logger.info("Telegram bot application created successfully")
    return _application


async def start_bot():
    """Start the bot polling."""
    app = create_bot()
    
    logger.info("Starting Telegram bot...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    logger.info("Telegram bot started successfully")


async def stop_bot():
    """Stop the bot."""
    global _application
    
    if _application:
        logger.info("Stopping Telegram bot...")
        await _application.updater.stop()
        await _application.stop()
        await _application.shutdown()
        _application = None
        logger.info("Telegram bot stopped")
