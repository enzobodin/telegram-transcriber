import logging
import os
from typing import BinaryIO
import ffmpeg
import numpy as np
import telebot
from faster_whisper import WhisperModel
import time

bot_id = os.getenv("BOT_ID")
model_name = os.getenv("ASR_MODEL", "small")
allowed_users = os.environ['ALLOWED_USERS']
precision = os.getenv("PRECISION", "int8")

bot = telebot.TeleBot(bot_id)
model = WhisperModel(model_name, device="cpu", compute_type=precision)
SAMPLE_RATE = 16000

@bot.message_handler(
    content_types=["voice"],
    chat_types=["private", "group", "supergroup"],
)
def transcribe_voice_message(message):
    start_time = time.time()
    u_id=message.chat.username
    if u_id in allowed_users:
        voice_meta = bot.get_file(message.voice.file_id)
        voice_audio = load_audio(bot.download_file(voice_meta.file_path))
        segments, _ = model.transcribe(audio=voice_audio, vad_filter=True)
        final_time = time.time()
        processing_time = (final_time - start_time)
        text = "".join([segment.text for segment in segments])
        result = f"▶️ {text}\n⌛ *Processing time*: {processing_time:.4f} seconds\n🪄 *ASR_Model*: {model_name}"
        bot.reply_to(message, result, parse_mode='Markdown')

    else:
        bot.reply_to(message, "Vous n'avez pas la permission d'utiliser le bot")

def load_audio(binary_file: BinaryIO, sr: int = SAMPLE_RATE):
    try:
        out, _ = (
            ffmpeg.input("pipe:", threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=binary_file)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0


logging.warning("Start polling")
bot.infinity_polling(timeout=10, long_polling_timeout=5)