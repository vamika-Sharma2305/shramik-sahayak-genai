FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY api ./api

EXPOSE 10000
CMD ["sh", "-c", "uvicorn app.agent_pipeline:app --host 0.0.0.0 --port ${PORT:-10000}"]