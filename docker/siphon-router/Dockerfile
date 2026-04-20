FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi==0.115.12 \
    uvicorn[standard]==0.34.2 \
    httpx==0.28.1 \
    redis==5.2.1 \
    pydantic==2.11.3

COPY siphon /app/siphon

EXPOSE 5010

CMD ["python", "-m", "siphon.server"]

