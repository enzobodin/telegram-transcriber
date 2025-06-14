FROM python:3.13.5-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    ffmpeg flac

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]
