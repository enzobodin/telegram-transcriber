FROM python:3.10.11-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    ffmpeg

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]
