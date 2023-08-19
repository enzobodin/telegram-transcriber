import logging, os, telebot, time
import speech_recognition as sr
from pydub import AudioSegment

bot_id = os.getenv("BOT_ID")
allowed_users = os.environ['ALLOWED_USERS']

bot = telebot.TeleBot(bot_id)

@bot.message_handler(
    content_types=["voice"],
    chat_types=["private", "group", "supergroup"],
)
def transcribe_voice_message(message):
    start_time = time.time()
    u_id=message.chat.username
    if u_id in allowed_users:
        voice_meta = bot.get_file(message.voice.file_id)
        voice_audio = bot.download_file(voice_meta.file_path)
        with open('audiovoice.ogg', 'wb') as f:
            f.write(voice_audio)
        audio = AudioSegment.from_file("audiovoice.ogg", format='ogg')
        audio.export('audio.wav', format='wav')
        with sr.AudioFile('audio.wav') as source:
            audio_data = sr.Recognizer().record(source)
            text = sr.Recognizer().recognize_google(audio_data, language="fr-FR")
        final_time = time.time()
        processing_time = (final_time - start_time)
        result = f"▶️ {text}\n⌛ *Processing time*: {processing_time:.4f} seconds"
        bot.reply_to(message, result, parse_mode='Markdown')

    else:
        bot.reply_to(message, "Vous n'avez pas la permission d'utiliser le bot")

logging.warning("Start polling")
bot.infinity_polling(timeout=10, long_polling_timeout=5)