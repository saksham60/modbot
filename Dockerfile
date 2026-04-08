FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    HOST=0.0.0.0

WORKDIR /app

COPY pyproject.toml README.md openenv.yaml requirements.txt /app/
COPY modbot /app/modbot

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir . && \
    chmod +x modbot/deployment/start.sh

EXPOSE 7860

CMD ["bash", "modbot/deployment/start.sh"]
