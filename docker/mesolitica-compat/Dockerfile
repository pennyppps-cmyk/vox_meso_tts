FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi==0.115.12 uvicorn[standard]==0.34.2 httpx==0.28.1

COPY services/mesolitica_compat /app

EXPOSE 5001

CMD ["python", "main.py"]

