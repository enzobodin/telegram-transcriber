import logging
import os
import time
from typing import BinaryIO
import requests
import telebot
import speech_recognition as sr
from pydub import AudioSegment
from faster_whisper import WhisperModel
import ffmpeg
import numpy as np

bot_id = os.getenv("BOT_ID")
allowed_users = os.environ['ALLOWED_USERS']
precision = os.getenv("PRECISION", "int8")
model_name = os.getenv("ASR_MODEL", "small")
mode = os.getenv("MODE")
model = WhisperModel(model_name, device="cpu", compute_type=precision) if mode == "faster_whisper" else None
whisper_server_url = os.getenv("WHISPER_SERVER_URL")

bot = telebot.TeleBot(bot_id)

def google_mode(voice_audio):
    start_time = time.time()
    with open('audiovoice.ogg', 'wb') as f:
        f.write(voice_audio)
    audio = AudioSegment.from_file("audiovoice.ogg", format='ogg')
    audio.export('audio.wav', format='wav')
    with sr.AudioFile('audio.wav') as source:
        audio_data = sr.Recognizer().record(source)
        text = sr.Recognizer().recognize_google(audio_data, language="fr-FR")
    processing_time = time.time() - start_time
    result = f"▶️ {text}\n⌛ *Processing time*: {processing_time:.4f} seconds"
    return result

def whisper_mode(voice_audio):
    start_time = time.time()
    voice = load_audio(voice_audio)
    segments, _ = model.transcribe(audio=voice, vad_filter=True)
    processing_time = time.time() - start_time
    text = "".join([segment.text for segment in segments])
    result = f"▶️ {text}\n⌛ *Processing time*: {processing_time:.4f} seconds\n🪄 *ASR_Model*: {model_name}"
    return result

def whisper_server_mode(voice_audio):
    start_time = time.time()
    response = requests.post(
        f"{whisper_server_url}/asr",
        files={'audio_file': ('audio.ogg', voice_audio)},
        params = {'output': 'json'},
        timeout=30
    )
    response.raise_for_status()
    text = response.json().get("text", "")
    processing_time = time.time() - start_time
    result = f"▶️ {text}\n⌛ *Processing time*: {processing_time:.4f} seconds\n🌐 *Whisper Server*"
    return result

def load_audio(binary_file: BinaryIO):
    try:
        out, _ = (
            ffmpeg.input("pipe:", threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=16000)
            .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=binary_file)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

@bot.message_handler(
    content_types=["voice"],
    chat_types=["private", "group", "supergroup"],
)
def transcribe_voice_message(message):
    u_id = message.chat.username
    if u_id in allowed_users:
        voice_meta = bot.get_file(message.voice.file_id)
        voice_audio = bot.download_file(voice_meta.file_path)

        if mode == "google":
            result = google_mode(voice_audio)
        elif mode == "faster_whisper":
            result = whisper_mode(voice_audio)
        elif mode == "whisper_server":
            result = whisper_server_mode(voice_audio)
        else:
            result = "Invalid mode, select either faster_whisper, google, or whisper_server in your deployment configuration"

        bot.reply_to(message, result, parse_mode='Markdown')
    else:
        bot.reply_to(message, "Vous n'avez pas la permission d'utiliser le bot")

logging.warning("Start polling")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
