FROM python:3.11-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install --upgrade pip

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python", "server.py"]