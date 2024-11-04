# telegram-transcriber 
Based on https://github.com/ckaytev/tgisper  
Using Google Speech Recognition and OpenAI Whisper model.

## Variables
    - `BOT_ID`: Your Telegram bot token
    - `ALLOWED_USERS`: Comma-separated list of allowed user IDs
    - `PRECISION` (optional): Precision level for the ASR model (default: `int8`)
    - `ASR_MODEL` (optional): Name of the ASR model to use (default: `small`)
    - `MODE`: ASR mode to use (`whisper` or `google`)

## How to run
Update variables in docker-compose.yml and run it

## TO DO
- [ ] Add remote whisper server
