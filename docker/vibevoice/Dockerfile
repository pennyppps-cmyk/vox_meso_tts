FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    fastapi==0.115.12 \
    uvicorn[standard]==0.34.2 \
    pydantic==2.11.3 \
    numpy==2.0.2 \
    soundfile==0.13.1 \
    torch==2.6.0 \
    torchaudio==2.6.0 \
    transformers==4.51.3

COPY services/vibevoice /app

EXPOSE 5003

CMD ["python3", "main.py"]

