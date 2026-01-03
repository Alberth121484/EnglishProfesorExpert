import logging
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from app.database import AsyncSessionLocal
from app.services import StudentService, LessonService, SpeechService
from app.agent import get_tutor_response
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
speech_service = SpeechService()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    
    async with AsyncSessionLocal() as db:
        student_service = StudentService(db)
        student, is_new = await student_service.get_or_create_student(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code or "es"
        )
        logger.info(f"Start command - Student {'created' if is_new else 'found'}: {student.id} (telegram_id: {user.id})")
        
        # Ensure student is committed to database
        await db.commit()
        
        if is_new:
            welcome_message = (
                f"¡Hola {student.first_name}! 👋\n\n"
                "Soy tu tutor de inglés personal. Estoy aquí para ayudarte "
                "a aprender inglés desde cero hasta un nivel avanzado.\n\n"
                "🎯 Tu nivel actual: *Pre A1 - Principiante*\n\n"
                "Puedes:\n"
                "• Enviarme mensajes de texto\n"
                "• Enviarme notas de voz\n"
                "• Usar /progress para ver tu progreso\n"
                "• Usar /help para más comandos\n\n"
                "¡Empecemos! Escríbeme 'Hello' para comenzar tu primera lección."
            )
        else:
            welcome_message = (
                f"¡Hola de nuevo, {student.first_name}! 👋\n\n"
                f"🎯 Tu nivel actual: *{student.current_level.name}*\n"
                f"🔥 Racha: {student.streak_days} días\n"
                f"📚 Lecciones completadas: {student.total_lessons}\n\n"
                "¿Listo para continuar aprendiendo? ¡Envíame un mensaje!"
            )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📖 *Comandos disponibles:*\n\n"
        "/start - Iniciar o reiniciar el bot\n"
        "/progress - Ver tu progreso detallado\n"
        "/level - Ver información de tu nivel actual\n"
        "/panel - Obtener enlace a tu panel de progreso\n"
        "/help - Mostrar esta ayuda\n\n"
        "💡 *Consejos:*\n"
        "• Puedes enviarme texto o notas de voz\n"
        "• Responderé siempre con audio para practicar tu escucha\n"
        "• ¡Practica todos los días para mantener tu racha!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /progress command."""
    user = update.effective_user
    
    async with AsyncSessionLocal() as db:
        student_service = StudentService(db)
        student = await student_service.get_student_by_telegram_id(user.id)
        
        if not student:
            await update.message.reply_text(
                "No encontré tu perfil. Usa /start para comenzar."
            )
            return
        
        # Build progress message
        skills_text = ""
        for skill in student.skills:
            bar = "█" * (skill.score // 10) + "░" * (10 - skill.score // 10)
            skills_text += f"• {skill.skill.name}: {bar} {skill.score}%\n"
        
        progress_message = (
            f"📊 *Tu Progreso - {student.full_name}*\n\n"
            f"🎯 Nivel: *{student.current_level.name}*\n"
            f"🔥 Racha: {student.streak_days} días\n"
            f"📚 Lecciones: {student.total_lessons}\n"
            f"⏱️ Tiempo total: {student.total_minutes} minutos\n\n"
            f"*Habilidades:*\n{skills_text}\n"
            f"💪 ¡Sigue practicando para subir de nivel!"
        )
    
    keyboard = [[
        InlineKeyboardButton("📱 Ver Panel Completo", url=f"{settings.frontend_url}?telegram_id={user.id}")
    ]]
    
    await update.message.reply_text(
        progress_message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def level_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /level command."""
    user = update.effective_user
    
    async with AsyncSessionLocal() as db:
        student_service = StudentService(db)
        student = await student_service.get_student_by_telegram_id(user.id)
        
        if not student:
            await update.message.reply_text(
                "No encontré tu perfil. Usa /start para comenzar."
            )
            return
        
        next_level = await student_service.get_next_level(student.current_level)
        next_level_text = f"Próximo nivel: *{next_level.name}*" if next_level else "¡Ya estás en el nivel máximo!"
        
        level_message = (
            f"🎯 *Tu Nivel Actual*\n\n"
            f"*{student.current_level.name}*\n\n"
            f"_{student.current_level.description}_\n\n"
            f"{next_level_text}\n\n"
            f"Para subir de nivel necesitas:\n"
            f"• Puntuación promedio ≥ 75%\n"
            f"• Al menos 10 lecciones en este nivel"
        )
    
    await update.message.reply_text(level_message, parse_mode="Markdown")


async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /panel command."""
    user = update.effective_user
    panel_url = f"{settings.frontend_url}?telegram_id={user.id}"
    
    keyboard = [[
        InlineKeyboardButton("🌐 Abrir Panel", url=panel_url)
    ]]
    
    await update.message.reply_text(
        "📱 Accede a tu panel de progreso completo:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    user = update.effective_user
    user_message = update.message.text
    
    # Send typing action
    await update.message.chat.send_action("typing")
    
    async with AsyncSessionLocal() as db:
        student_service = StudentService(db)
        lesson_service = LessonService(db)
        
        # Get or create student
        student, is_new = await student_service.get_or_create_student(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username
        )
        logger.info(f"Text handler - Student {'created' if is_new else 'found'}: {student.id} (telegram_id: {user.id})")
        
        # Ensure student is committed to database
        await db.commit()
        
        # Get or create active lesson
        lesson = await lesson_service.get_or_create_active_lesson(student)
        
        # Save user message
        await lesson_service.add_message(lesson, "user", user_message)
        
        # Get AI response
        response, evaluation = await get_tutor_response(
            telegram_id=user.id,
            student_id=student.id,
            student_name=student.first_name,
            current_level=student.current_level.code,
            current_level_id=student.current_level_id,
            total_lessons=student.total_lessons,
            streak_days=student.streak_days,
            user_input=user_message,
            lesson_id=lesson.id,
            is_new_student=is_new
        )
        
        # Save assistant message
        await lesson_service.add_message(lesson, "assistant", response)
        
        # Handle evaluation if present
        if evaluation:
            await lesson_service.update_lesson_evaluation(lesson, evaluation)
            await student_service.update_skill_scores(student, evaluation)
            
            # Check for level up
            new_level = await student_service.check_level_up(student)
            if new_level:
                response += f"\n\n🎉 ¡Felicidades! ¡Has subido a *{new_level.name}*!"
    
    # Send text response first
    await update.message.reply_text(response, parse_mode="Markdown")
    
    # Then generate and send audio response
    try:
        await update.message.chat.send_action("record_voice")
        audio_bytes = await speech_service.text_to_speech(response)
        
        # Send audio
        await update.message.reply_voice(voice=io.BytesIO(audio_bytes))
            
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        # Text already sent, just log the error


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages."""
    user = update.effective_user
    
    # Send typing action
    await update.message.chat.send_action("typing")
    
    try:
        # Get voice file
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        
        # Download and transcribe
        voice_bytes = await file.download_as_bytearray()
        user_message = await speech_service.transcribe_audio(bytes(voice_bytes))
        
        # Send transcription confirmation
        await update.message.reply_text(
            f"🎤 _Escuché: \"{user_message}\"_",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        await update.message.reply_text(
            "Lo siento, no pude procesar tu mensaje de voz. ¿Puedes intentar de nuevo?"
        )
        return
    
    async with AsyncSessionLocal() as db:
        student_service = StudentService(db)
        lesson_service = LessonService(db)
        
        # Get or create student
        student, is_new = await student_service.get_or_create_student(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username
        )
        logger.info(f"Voice handler - Student {'created' if is_new else 'found'}: {student.id} (telegram_id: {user.id})")
        
        # Ensure student is committed to database
        await db.commit()
        
        # Get or create active lesson
        lesson = await lesson_service.get_or_create_active_lesson(student)
        
        # Save user message
        await lesson_service.add_message(
            lesson, "user", user_message, audio_file_id=voice.file_id
        )
        
        # Get AI response
        response, evaluation = await get_tutor_response(
            telegram_id=user.id,
            student_id=student.id,
            student_name=student.first_name,
            current_level=student.current_level.code,
            current_level_id=student.current_level_id,
            total_lessons=student.total_lessons,
            streak_days=student.streak_days,
            user_input=user_message,
            lesson_id=lesson.id,
            is_audio=True,
            audio_file_id=voice.file_id,
            is_new_student=is_new
        )
        
        # Save assistant message
        await lesson_service.add_message(lesson, "assistant", response)
        
        # Handle evaluation if present
        if evaluation:
            await lesson_service.update_lesson_evaluation(lesson, evaluation)
            await student_service.update_skill_scores(student, evaluation)
            
            # Check for level up
            new_level = await student_service.check_level_up(student)
            if new_level:
                response += f"\n\n🎉 ¡Felicidades! ¡Has subido a *{new_level.name}*!"
    
    # Send text response first
    await update.message.reply_text(response, parse_mode="Markdown")
    
    # Then generate and send audio response
    try:
        await update.message.chat.send_action("record_voice")
        audio_bytes = await speech_service.text_to_speech(response)
        
        # Send audio
        await update.message.reply_voice(voice=io.BytesIO(audio_bytes))
            
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        # Text already sent, just log the error


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Error handling update: {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "Lo siento, ocurrió un error. Por favor intenta de nuevo."
        )


def setup_handlers(app: Application):
    """Setup all handlers for the bot."""
    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("progress", progress_command))
    app.add_handler(CommandHandler("level", level_command))
    app.add_handler(CommandHandler("panel", panel_command))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    logger.info("Telegram handlers configured")
