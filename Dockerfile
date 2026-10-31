
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DATA_FILE=/var/lib/backend_data/messages.json

WORKDIR /app

COPY app.py .

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3)" || exit 1

CMD ["python", "app.py"]
