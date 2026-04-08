FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copy files
COPY . /app

# install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# expose HF port
EXPOSE 7860

# run server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]