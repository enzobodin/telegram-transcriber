import logging, os, telebot, time
import speech_recognition as sr
from pydub import AudioSegment
from faster_whisper import WhisperModel
from typing import BinaryIO
import ffmpeg
import numpy as np

bot_id = os.getenv("BOT_ID")
allowed_users = os.environ['ALLOWED_USERS']
precision = os.getenv("PRECISION", "int8")
model_name = os.getenv("ASR_MODEL", "small")
mode = os.getenv("MODE")

bot = telebot.TeleBot(bot_id)

if mode == "whisper":
    model = WhisperModel(model_name, device="cpu", compute_type=precision)
elif mode == "google":
    pass
else:
    raise ValueError("Invalid mode, select either whisper or google")

def googleMode(voice_audio):
        start_time = time.time()
        with open('audiovoice.ogg', 'wb') as f:
            f.write(voice_audio)
        audio = AudioSegment.from_file("audiovoice.ogg", format='ogg')
        audio.export('audio.wav', format='wav')
        with sr.AudioFile('audio.wav') as source:
            audio_data = sr.Recognizer().record(source)
            text = sr.Recognizer().recognize_google(audio_data, language="fr-FR")
        processing_time = (time.time() - start_time)
        result = f"▶️ {text}\n⌛ *Processing time*: {processing_time:.4f} seconds"
        return result

def whisperMode(voice_audio):
    start_time = time.time()
    voice = load_audio(voice_audio)
    segments, _ = model.transcribe(audio=voice, vad_filter=True)
    processing_time = (time.time() - start_time)
    text = "".join([segment.text for segment in segments])
    result = f"▶️ {text}\n⌛ *Processing time*: {processing_time:.4f} seconds\n🪄 *ASR_Model*: {model_name}"
    return result

@bot.message_handler(
    content_types=["voice"],
    chat_types=["private", "group", "supergroup"],
)

def load_audio(binary_file: BinaryIO, sr: int = 16000):
    try:
        out, _ = (
            ffmpeg.input("pipe:", threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=binary_file)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

def transcribe_voice_message(message):
    u_id=message.chat.username
    if u_id in allowed_users:
        voice_meta = bot.get_file(message.voice.file_id)
        voice_audio = bot.download_file(voice_meta.file_path)

        if mode == "google":
            result = googleMode(voice_audio)
        elif mode == "whisper":
            result = whisperMode(voice_audio)

        bot.reply_to(message, result, parse_mode='Markdown')
    else:
        bot.reply_to(message, "Vous n'avez pas la permission d'utiliser le bot")

logging.warning("Start polling")
bot.infinity_polling(timeout=10, long_polling_timeout=5)