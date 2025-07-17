FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ffmpeg \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["python", "consumer.py"]