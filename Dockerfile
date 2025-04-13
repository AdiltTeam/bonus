FROM python:3.10-slim

# Sistem paketlərini qur
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-python-dev \
    libboost-thread-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    zlib1g-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# İşçi qovluğu
WORKDIR /app

# Faylları kopyala
COPY . /app

# Virtual environment yarat
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# Requirement-ləri quraşdır
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Port və startup
EXPOSE 5000
CMD ["python", "app.py"]
