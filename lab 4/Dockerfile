FROM python:3.12-slim

RUN useradd -ms /bin/bash appuser
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
USER appuser
EXPOSE 5000

CMD ["/bin/bash", "-lc", "if [ \"$FLASK_DEBUG\" = \"1\" ]; then \
      flask run --host=0.0.0.0 --port=5000; \
    else \
      exec gunicorn --bind 0.0.0.0:5000 app:app; \
    fi"]